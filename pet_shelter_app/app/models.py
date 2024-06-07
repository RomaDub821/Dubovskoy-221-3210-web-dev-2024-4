from . import db, login_manager
from flask_login import UserMixin
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    surname = db.Column(db.String(100), nullable=False)
    patronymic = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    address = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='user')
    preferences = db.Column(db.Text, nullable=True)
    password = db.Column(db.String(255), nullable=False)
    avatar = db.Column(db.String(100), nullable=True)
    shelter_id = db.Column(db.Integer, db.ForeignKey('shelter.id'), nullable=True)
    favorites = db.relationship('Favorites', back_populates='user', cascade='all, delete-orphan')
    shelter = db.relationship('Shelter', back_populates='users', foreign_keys=[shelter_id])

    def __repr__(self):
        return f"User('{self.name}', '{self.email}', '{self.role}')"


    
class Pet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    size = db.Column(db.String(50), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    color = db.Column(db.String(50), nullable=False)
    hair_length = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    partner_info = db.Column(db.Text, nullable=True)
    city = db.Column(db.String(100), nullable=False)
    availability = db.Column(db.Boolean, default=True)
    shelter_id = db.Column(db.Integer, db.ForeignKey('shelter.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    image_file = db.Column(db.String(100), nullable=True)
    favorites = db.relationship('Favorites', back_populates='pet', cascade='all, delete-orphan')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"Pet('{self.name}', '{self.city}', '{self.price}')"

class Avatar(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    hash = db.Column(db.String(255), nullable=False)

class Shelter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    zip_code = db.Column(db.String(20), nullable=False)
    pets = db.relationship('Pet', backref='shelter', lazy=True)
    users = db.relationship('User', back_populates='shelter')


class Favorites(db.Model):
    __tablename__ = 'favorites'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True)
    pet_id = db.Column(db.Integer, db.ForeignKey('pet.id', ondelete='CASCADE'), primary_key=True)
    user = db.relationship('User', back_populates='favorites')
    pet = db.relationship('Pet', back_populates='favorites')

