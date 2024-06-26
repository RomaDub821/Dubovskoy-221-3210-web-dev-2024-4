from typing import Optional
from flask_wtf import FlaskForm
from wtforms import FileField, StringField, PasswordField, SubmitField, BooleanField, IntegerField, SelectField, TextAreaField, DecimalField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app.models import Shelter, User
from wtforms.validators import DataRequired, Length, Email, EqualTo, Optional, NumberRange
from flask_wtf.file import FileAllowed


class RegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=50)])
    surname = StringField('Surname', validators=[DataRequired(), Length(min=2, max=50)])
    patronymic = StringField('Patronymic', validators=[DataRequired(), Length(min=2, max=50)])
    phone_number = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=15)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    address = StringField('Address', validators=[DataRequired(), Length(min=5, max=100)])
    city = StringField('City', validators=[DataRequired(), Length(min=2, max=50)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Role', choices=[('user', 'User'), ('representative', 'Representative'), ('moderator', 'Moderator')], validators=[DataRequired()])
    shelter = SelectField('Shelter', coerce=int, validators=[Optional()])
    preferences = TextAreaField('Preferences', validators=[Optional(), Length(max=200)])
    submit = SubmitField('Sign Up')

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.shelter.choices = [(shelter.id, shelter.name) for shelter in Shelter.query.all()]

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')
        

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class AddPetForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    size = StringField('Size', validators=[DataRequired(), Length(min=1, max=50)])
    age = IntegerField('Age', validators=[DataRequired()])
    color = StringField('Color', validators=[DataRequired(), Length(min=2, max=50)])
    hair_length = StringField('Hair Length', validators=[DataRequired(), Length(min=2, max=50)])
    gender = SelectField('Gender', choices=[('male', 'Male'), ('female', 'Female')], validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    price = DecimalField('Price', validators=[DataRequired()])
    partner_info = TextAreaField('Partner Info', validators=[Optional(), Length(max=200)])
    city = StringField('City', validators=[DataRequired(), Length(min=2, max=100)])
    availability = SelectField('Availability', choices=[(1, 'Available'), (0, 'Not Available')], coerce=int, validators=[DataRequired()])
    shelter_id = SelectField('Shelter', coerce=int, validators=[DataRequired()])
    image_file = FileField('Upload Image', validators=[Optional(), FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Images only!')])
    submit = SubmitField('Add Pet')

class AddShelterForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    phone_number = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    address = StringField('Address', validators=[DataRequired(), Length(min=5, max=200)])
    city = StringField('City', validators=[DataRequired(), Length(min=2, max=100)])
    zip_code = StringField('Zip Code', validators=[DataRequired(), Length(min=5, max=20)])
    submit = SubmitField('Add Shelter')

class EditUserForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=50)])
    surname = StringField('Surname', validators=[DataRequired(), Length(min=2, max=50)])
    patronymic = StringField('Patronymic', validators=[DataRequired(), Length(min=2, max=50)])
    phone_number = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=15)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    address = StringField('Address', validators=[DataRequired(), Length(min=5, max=100)])
    city = StringField('City', validators=[DataRequired(), Length(min=2, max=50)])
    role = SelectField('Role', choices=[('user', 'User'), ('representative', 'Representative'), ('moderator', 'Moderator')], validators=[DataRequired()])
    preferences = TextAreaField('Preferences', validators=[Optional(), Length(max=200)])
    shelter_id = SelectField('Shelter', coerce=int, validators=[Optional()])
    submit = SubmitField('Save Changes')

class FilterPetsForm(FlaskForm):
    age = IntegerField('Age', validators=[Optional()])
    size = StringField('Size', validators=[Optional(), Length(min=1, max=50)])
    color = StringField('Color', validators=[Optional(), Length(min=2, max=50)])
    gender = SelectField('Gender', choices=[('', 'Любой'), ('male', 'Мальчик'), ('female', 'Девочка')], validators=[Optional()])
    price_min = DecimalField('Min Price', validators=[Optional(), NumberRange(min=0)])
    price_max = DecimalField('Max Price', validators=[Optional(), NumberRange(min=0)])
    sort_by = SelectField('Sort By', choices=[
        ('age_asc', 'Возраст: От младшего к старшему'),
        ('age_desc', 'Возраст: От старшего к младшему'),
        ('created_at_asc', 'Дата добавления: От старой к новой'),
        ('created_at_desc', 'Дата добавления: От новой к старой')
    ], validators=[Optional()])
    submit = SubmitField('Apply Filters')
class UploadAvatarForm(FlaskForm):
    avatar = FileField('Upload Avatar', validators=[DataRequired()])
    submit = SubmitField('Upload')
