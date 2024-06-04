import os
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.utils import secure_filename
from app import db, bcrypt
from app.models import User, Pet, Shelter
from app.forms import RegistrationForm, LoginForm, EditUserForm, AddPetForm, UploadAvatarForm, AddShelterForm

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_user = User(
            name=form.name.data,
            surname=form.surname.data,
            patronymic=form.patronymic.data,
            phone_number=form.phone_number.data,
            email=form.email.data,
            address=form.address.data,
            city=form.city.data,
            password=hashed_password,
            role=form.role.data,
            preferences=form.preferences.data
        )
        db.session.add(new_user)
        db.session.commit()
        flash('Ваш аккаунт был создан!', 'success')
        return redirect(url_for('main.index'))
    return render_template('register.html', title='Регистрация', form=form)

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
        db.session.commit()
        flash('User updated successfully', 'success')
        return redirect(url_for('auth.manage_users'))

    return render_template('edit_user.html', form=form, user=user)

@auth_bp.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    user = current_user
    pets = Pet.query.filter_by(user_id=user.id).all() if user.role in ['representative', 'moderator'] else []
    edit_form = EditUserForm(obj=user)
    avatar_form = UploadAvatarForm()

    if edit_form.validate_on_submit() and 'edit_user' in request.form:
        user.name = edit_form.name.data
        user.surname = edit_form.surname.data
        user.patronymic = edit_form.patronymic.data
        user.phone_number = edit_form.phone_number.data
        user.email = edit_form.email.data
        user.address = edit_form.address.data
        user.city = edit_form.city.data
        user.preferences = edit_form.preferences.data
        db.session.commit()
        flash('Account updated successfully', 'success')
        return redirect(url_for('auth.account'))

    if avatar_form.validate_on_submit() and 'upload_avatar' in request.form:
        avatar = avatar_form.avatar.data
        filename = secure_filename(avatar.filename)
        avatar.save(os.path.join('path/to/save', filename))
        user.avatar_id = filename
        db.session.commit()
        flash('Avatar updated successfully', 'success')
        return redirect(url_for('auth.account'))

    return render_template('account.html', user=user, edit_form=edit_form, avatar_form=avatar_form, pets=pets)

@auth_bp.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if current_user.role != 'moderator':
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))

    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully', 'success')
    return redirect(url_for('auth.manage_users'))

@auth_bp.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
    user = current_user
    db.session.delete(user)
    db.session.commit()
    flash('Account deleted successfully', 'success')
    return redirect(url_for('main.index'))

@auth_bp.route('/manage_users', methods=['GET', 'POST'])
@login_required
def manage_users():
    if current_user.role != 'moderator':
        flash('Access denied', 'danger')
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
    if current_user.role not in ['representative', 'moderator']:
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))

    form = AddShelterForm()
    if form.validate_on_submit():
        new_shelter = Shelter(
            name=form.name.data,
            phone_number=form.phone_number.data,
            email=form.email.data,
            address=form.address.data,
            city=form.city.data,
            zip_code=form.zip_code.data
        )
        db.session.add(new_shelter)
        db.session.commit()
        flash('Shelter added successfully', 'success')
        return redirect(url_for('auth.manage_shelters'))
    return render_template('add_shelter.html', form=form)

@auth_bp.route('/manage_shelters', methods=['GET'])
@login_required
def manage_shelters():
    if current_user.role not in ['representative', 'moderator']:
        flash('Access denied', 'danger')
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
