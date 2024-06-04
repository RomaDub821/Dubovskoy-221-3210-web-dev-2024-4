from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models import Favorites, Pet, Shelter, User
from app.forms import AddPetForm, AddShelterForm, EditUserForm, FilterPetsForm

main = Blueprint('main', __name__)

@main.route('/', methods=['GET', 'POST'])
def index():
    form = FilterPetsForm()
    query = Pet.query

    if form.validate_on_submit():
        if form.age.data:
            query = query.filter(Pet.age == form.age.data)
        if form.size.data:
            query = query.filter(Pet.size.like(f"%{form.size.data}%"))
        if form.color.data:
            query = query.filter(Pet.color.like(f"%{form.color.data}%"))
        if form.gender.data:
            query = query.filter(Pet.gender == form.gender.data)
        if form.price_min.data:
            query = query.filter(Pet.price >= form.price_min.data)
        if form.price_max.data:
            query = query.filter(Pet.price <= form.price_max.data)

    pets = query.all()
    return render_template('index.html', pets=pets, form=form)

@main.route('/favorites')
@login_required
def favorites():
    user = current_user
    favorites = Favorites.query.filter_by(user_id=user.id).all()
    return render_template('favorites.html', favorites=favorites)

@main.route('/add_pet', methods=['GET', 'POST'])
@login_required
def add_pet():
    if current_user.role != 'representative':
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))
    form = AddPetForm()
    if form.validate_on_submit():
        pet = Pet(
            name=form.name.data,
            size=form.size.data,
            age=form.age.data,
            color=form.color.data,
            hair_length=form.hair_length.data,
            gender=form.gender.data,
            description=form.description.data,
            price=form.price.data,
            partner_info=form.partner_info.data,
            city=form.city.data,
            availability=form.availability.data,
            shelter_id=form.shelter_id.data,
            user_id=current_user.id
        )
        db.session.add(pet)
        db.session.commit()
        flash('Питомец добавлен!', 'success')
        return redirect(url_for('main.index'))
    return render_template('add_pet.html', form=form)

@main.route('/add_shelter', methods=['GET', 'POST'])
@login_required
def add_shelter():
    if current_user.role not in ['moderator', 'representative']:
        flash('У вас нет доступа для добавления приюта.', 'danger')
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

@main.route('/manage_users')
@login_required
def manage_users():
    if current_user.role != 'moderator':
        flash('У вас нет доступа для просмотра этой страницы.', 'danger')
        return redirect(url_for('main.index'))
    
    users = User.query.all()
    return render_template('manage_users.html', users=users)

@main.route('/user/<int:user_id>')
@login_required
def view_user(user_id):
    if current_user.role != 'moderator':
        flash('У вас нет доступа для просмотра этой страницы.', 'danger')
        return redirect(url_for('main.index'))
    
    user = User.query.get_or_404(user_id)
    return render_template('view_user.html', user=user)

@main.route('/user/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if current_user.role != 'moderator':
        flash('У вас нет доступа для редактирования этой страницы.', 'danger')
        return redirect(url_for('main.index'))
    
    user = User.query.get_or_404(user_id)
    form = EditUserForm(obj=user)
    if form.validate_on_submit():
        form.populate_obj(user)
        db.session.commit()
        flash('Информация о пользователе обновлена!', 'success')
        return redirect(url_for('main.manage_users'))
    return render_template('edit_user.html', form=form, user=user)

@main.route('/user/<int:user_id>/delete', methods=['POST'])
@login_required
def delete_user(user_id):
    if current_user.role != 'moderator':
        flash('У вас нет доступа для удаления пользователя.', 'danger')
        return redirect(url_for('main.index'))
    
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('Пользователь удален!', 'success')
    return redirect(url_for('main.manage_users'))
