import os
from flask import Blueprint, current_app, render_template, redirect, url_for, flash, request
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.utils import secure_filename
from app import db, bcrypt
from app.models import User, Pet, Shelter
from app.forms import RegistrationForm, LoginForm, EditUserForm, AddPetForm, UploadAvatarForm, AddShelterForm

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        shelter_id = form.shelter.data if form.role.data == 'representative' else None
        user = User(
            name=form.name.data,
            surname=form.surname.data,
            patronymic=form.patronymic.data,
            phone_number=form.phone_number.data,
            email=form.email.data,
            address=form.address.data,
            city=form.city.data,
            password=hashed_password,
            role=form.role.data,
            shelter_id=shelter_id,
            preferences=form.preferences.data
        )
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created!', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html', title='Register', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            flash('Вы успешно вошли в аккаунт!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.index'))
        else:
            flash('Ошибка входа. Пожалуйста, проверьте email и пароль', 'danger')
    return render_template('login.html', title='Вход', form=form)

@auth_bp.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if current_user.role != 'moderator':
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))

    user = User.query.get_or_404(user_id)
    form = EditUserForm(obj=user)
    
    shelters = Shelter.query.all()
    form.shelter_id.choices = [(shelter.id, shelter.name) for shelter in shelters] if shelters else []

    if form.validate_on_submit():
        user.name = form.name.data
        user.surname = form.surname.data
        user.patronymic = form.patronymic.data
        user.phone_number = form.phone_number.data
        user.email = form.email.data
        user.address = form.address.data
        user.city = form.city.data
        user.role = form.role.data
        user.preferences = form.preferences.data
        user.shelter_id = form.shelter_id.data if form.shelter_id.data else None
        db.session.commit()
        flash('Пользователь успешно обновлен', 'success')
        return redirect(url_for('auth.manage_users'))

    return render_template('edit_user.html', form=form, user=user)

@auth_bp.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    user = current_user
    pets = Pet.query.filter_by(user_id=user.id).all() if user.role in ['representative', 'moderator'] else []
    edit_form = EditUserForm(obj=user)
    avatar_form = UploadAvatarForm()

    if user.role == 'representative':
        shelters = Shelter.query.all()
        edit_form.shelter_id.choices = [(shelter.id, shelter.name) for shelter in shelters]
    else:
        edit_form.shelter_id.choices = [] 

    if edit_form.validate_on_submit() and 'edit_user' in request.form:
        user.name = edit_form.name.data
        user.surname = edit_form.surname.data
        user.patronymic = edit_form.patronymic.data
        user.phone_number = edit_form.phone_number.data
        user.email = edit_form.email.data
        user.address = edit_form.address.data
        user.city = edit_form.city.data
        user.preferences = edit_form.preferences.data
        user.role = edit_form.role.data
        if user.role == 'representative' and edit_form.shelter_id.data:
            user.shelter_id = edit_form.shelter_id.data
        else:
            user.shelter_id = None  
        db.session.commit()
        flash('Аккаунт успешно обновлен', 'success')
        return redirect(url_for('auth.account'))

    if avatar_form.validate_on_submit() and 'upload_avatar' in request.form:
        avatar = avatar_form.avatar.data
        filename = secure_filename(avatar.filename)
        avatar.save(os.path.join(current_app.config['UPLOADED_PHOTOS_DEST'], filename))
        user.avatar = filename
        db.session.commit()
        flash('Аватарка успешно загружена', 'success')
        return redirect(url_for('auth.account'))

    return render_template('account.html', user=user, edit_form=edit_form, avatar_form=avatar_form, pets=pets)

@auth_bp.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if current_user.role != 'moderator':
        flash('Доступ запрещен', 'danger')
        return redirect(url_for('auth.manage_users'))
    
    pets = Pet.query.filter_by(user_id=user_id).all()
    for pet in pets:
        pet.user_id = None
        db.session.add(pet)
    
    db.session.delete(user)
    db.session.commit()
    flash('Пользователь удален, питомцы отвязаны!', 'success')
    return redirect(url_for('auth.manage_users'))

@auth_bp.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
    user = current_user
    db.session.delete(user)
    db.session.commit()
    flash('Аккаунт успешно удален', 'success')
    return redirect(url_for('main.index'))

@auth_bp.route('/manage_users', methods=['GET', 'POST'])
@login_required
def manage_users():
    if current_user.role != 'moderator':
        flash('Доступ запрещен', 'danger')
        return redirect(url_for('main.index'))

    users = User.query.all()
    return render_template('manage_users.html', users=users)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы успешно вышли из аккаунта!', 'success')
    return redirect(url_for('main.index'))

@auth_bp.route('/add_shelter', methods=['GET', 'POST'])
@login_required
def add_shelter():
    if current_user.role != 'moderator':
        flash('Доступ запрещен', 'danger')
        return redirect(url_for('main.index'))

    form = AddShelterForm()
    if form.validate_on_submit():
        shelter = Shelter(
            name=form.name.data,
            phone_number=form.phone_number.data,
            email=form.email.data,
            address=form.address.data,
            city=form.city.data,
            zip_code=form.zip_code.data
        )
        db.session.add(shelter)
        db.session.commit()
        flash('Приют добавлен!', 'success')
        return redirect(url_for('main.index'))
    return render_template('add_shelter.html', form=form)

@auth_bp.route('/manage_shelters', methods=['GET'])
@login_required
def manage_shelters():
    if current_user.role not in ['representative', 'moderator']:
        flash('Доступ запрещен', 'danger')
        return redirect(url_for('main.index'))

    shelters = Shelter.query.all()
    return render_template('manage_shelters.html', shelters=shelters)

@auth_bp.route('/add_to_favorites/<int:pet_id>', methods=['POST'])
@login_required
def add_to_favorites(pet_id):
    pet = Pet.query.get_or_404(pet_id)
    current_user.favorites.append(pet)
    db.session.commit()
    flash('Питомец добавлен в избранное!', 'success')
    return redirect(url_for('main.index'))

@auth_bp.route('/favorites')
@login_required
def favorites():
    pets = current_user.favorites
    return render_template('favorites.html', pets=pets)
