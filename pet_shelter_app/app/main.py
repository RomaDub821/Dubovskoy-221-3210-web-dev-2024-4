import os
from flask import Blueprint, current_app, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models import Favorites, Pet, Shelter, User
from app.forms import AddPetForm, AddShelterForm, EditUserForm, FilterPetsForm
from werkzeug.utils import secure_filename
import os
from flask import Blueprint, current_app, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.models import Pet, Shelter
from app.forms import AddPetForm
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

    page = request.args.get('page', 1, type=int)
    pets = query.paginate(page=page, per_page=9)

    return render_template('index.html', pets=pets.items, form=form, pagination=pets)

@main.route('/pet/<int:pet_id>')
def pet_details(pet_id):
    pet = Pet.query.get_or_404(pet_id)
    return render_template('pet_details.html', pet=pet)



@main.route('/favorites')
@login_required
def favorites():
    user = current_user
    favorites = Favorites.query.filter_by(user_id=user.id).all()
    return render_template('favorites.html', favorites=favorites)

@main.route('/add_pet', methods=['GET', 'POST'])
@login_required
def add_pet():
    if current_user.role not in ['representative', 'moderator']:
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))

    shelters = Shelter.query.all()
    form = AddPetForm()
    form.shelter_id.choices = [(shelter.id, shelter.name) for shelter in shelters]

    if form.validate_on_submit():
        filename = None
        if form.image_file.data:
            filename = secure_filename(form.image_file.data.filename)
            form.image_file.data.save(os.path.join(current_app.config['UPLOADED_PHOTOS_DEST'], filename))

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
            user_id=current_user.id,
            image_file=filename
        )
        db.session.add(pet)
        db.session.commit()
        flash('Питомец добавлен!', 'success')
        return redirect(url_for('main.index'))
    return render_template('add_pet.html', form=form)


@main.route('/edit_pet/<int:pet_id>', methods=['GET', 'POST'])
@login_required
def edit_pet(pet_id):
    pet = Pet.query.get_or_404(pet_id)
    if current_user.role != 'moderator' and (current_user.role == 'representative' and pet.shelter_id != current_user.shelter_id):
        flash('У вас нет доступа для редактирования этого питомца.', 'danger')
        return redirect(url_for('main.index'))

    form = AddPetForm(obj=pet)
    shelters = Shelter.query.all()
    form.shelter_id.choices = [(shelter.id, shelter.name) for shelter in shelters]

    if form.validate_on_submit():
        pet.name = form.name.data
        pet.size = form.size.data
        pet.age = form.age.data
        pet.color = form.color.data
        pet.hair_length = form.hair_length.data
        pet.gender = form.gender.data
        pet.description = form.description.data
        pet.price = form.price.data
        pet.partner_info = form.partner_info.data
        pet.city = form.city.data
        pet.availability = form.availability.data
        pet.shelter_id = form.shelter_id.data
        if form.image_file.data:
            filename = secure_filename(form.image_file.data.filename)
            form.image_file.data.save(os.path.join(current_app.config['UPLOADED_PHOTOS_DEST'], filename))
            pet.image_file = filename
        db.session.commit()
        flash('Питомец обновлен!', 'success')
        return redirect(url_for('main.pet_details', pet_id=pet.id))

    return render_template('edit_pet.html', form=form, pet=pet)

@main.route('/delete_pet/<int:pet_id>', methods=['POST'])
@login_required
def delete_pet(pet_id):
    pet = Pet.query.get_or_404(pet_id)
    if current_user.role == 'moderator' or (current_user.role == 'representative' and pet.shelter_id == current_user.shelter_id):
        db.session.delete(pet)
        db.session.commit()
        flash('Питомец удален!', 'success')
        return redirect(url_for('main.index'))
    else:
        flash('У вас нет прав для удаления этого питомца.', 'danger')
        return redirect(url_for('main.index'))




@main.route('/add_to_favorites/<int:pet_id>', methods=['POST'])
@login_required
def add_to_favorites(pet_id):
    pet = Pet.query.get_or_404(pet_id)
    favorite = Favorites.query.filter_by(user_id=current_user.id, pet_id=pet_id).first()
    if favorite:
        flash('Питомец уже добавлен в избранное!', 'info')
    else:
        favorite = Favorites(user_id=current_user.id, pet_id=pet_id)
        db.session.add(favorite)
        db.session.commit()
        flash('Питомец добавлен в избранное!', 'success')
    return redirect(url_for('main.index'))



@main.route('/add_shelter', methods=['GET', 'POST'])
@login_required
def add_shelter():
    if current_user.role != 'moderator':
        flash('Access denied', 'danger')
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
        flash('Shelter added successfully!', 'success')
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


@main.route('/remove_from_favorites/<int:pet_id>', methods=['POST'])
@login_required
def remove_from_favorites(pet_id):
    favorite = Favorites.query.filter_by(user_id=current_user.id, pet_id=pet_id).first()
    if favorite:
        db.session.delete(favorite)
        db.session.commit()
        flash('Питомец удален из избранного!', 'success')
    else:
        flash('Питомец не найден в избранном!', 'danger')
    return redirect(url_for('main.favorites'))
