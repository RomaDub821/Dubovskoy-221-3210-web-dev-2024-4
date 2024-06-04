from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import Pet, User, Favorites
from app.forms import AddPetForm
from app import db

main = Blueprint('main', __name__)

@main.route('/')
def index():
    pets = Pet.query.all()
    return render_template('index.html', pets=pets)

@main.route('/add_pet', methods=['GET', 'POST'])
@login_required
def add_pet():
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
            user_id=current_user.id
        )
        db.session.add(pet)
        db.session.commit()
        flash('Питомец добавлен!', 'success')
        return redirect(url_for('main.index'))
    return render_template('add_pet.html', form=form)

@main.route('/pet/<int:pet_id>')
def pet_details(pet_id):
    pet = Pet.query.get_or_404(pet_id)
    return render_template('pet_details.html', pet=pet)

@main.route('/edit_pet/<int:pet_id>', methods=['GET', 'POST'])
@login_required
def edit_pet(pet_id):
    pet = Pet.query.get_or_404(pet_id)
    form = AddPetForm()
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
        db.session.commit()
        return redirect(url_for('main.pet_details', pet_id=pet.id))
    elif request.method == 'GET':
        form.name.data = pet.name
        form.size.data = pet.size
        form.age.data = pet.age
        form.color.data = pet.color
        form.hair_length.data = pet.hair_length
        form.gender.data = pet.gender
        form.description.data = pet.description
        form.price.data = pet.price
        form.partner_info.data = pet.partner_info
        form.city.data = pet.city
        form.availability.data = pet.availability
        flash('Питомец добавлен!', 'success')
        return redirect(url_for('main.index'))
    return render_template('add_pet.html', form=form)

@main.route('/delete_pet/<int:pet_id>', methods=['POST'])
@login_required
def delete_pet(pet_id):
    pet = Pet.query.get_or_404(pet_id)
    db.session.delete(pet)
    db.session.commit()
    return redirect(url_for('main.index'))

@main.route('/add_to_favorites/<int:pet_id>', methods=['POST'])
@login_required
def add_to_favorites(pet_id):
    favorite = Favorites(user_id=current_user.id, pet_id=pet_id)
    db.session.add(favorite)
    db.session.commit()
    flash('Питомец добавлен в избранное!', 'success')
    return redirect(url_for('main.index'))

@main.route('/favorites')
@login_required
def favorites():
    favorites = Favorites.query.filter_by(user_id=current_user.id).all()
    return render_template('favorites.html', favorites=favorites)
