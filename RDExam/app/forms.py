from typing import Optional
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, SelectMultipleField, FileField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, NumberRange
from flask_wtf.file import FileAllowed
from app.models import Genre, Role

class BookForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Краткое описание', validators=[DataRequired()])
    year = IntegerField('Год', validators=[DataRequired(), NumberRange(min=1000, max=9999)])
    publisher = StringField('Издательство', validators=[DataRequired(), Length(max=100)])
    author = StringField('Автор', validators=[DataRequired(), Length(max=100)])
    pages = IntegerField('Объём (в страницах)', validators=[DataRequired()])
    genres = SelectMultipleField('Жанры', coerce=int)
    cover = FileField('Обложка', validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    submit = SubmitField('Сохранить')

    def __init__(self, *args, **kwargs):
        super(BookForm, self).__init__(*args, **kwargs)
        self.genres.choices = [(genre.id, genre.name) for genre in Genre.query.all()]

class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')
    
class RegistrationForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired()])
    patronymic = StringField('Отчество', validators=[Length(max=100)])
    role = SelectField('Роль', coerce=int)
    submit = SubmitField('Зарегистрироваться')

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name) for role in Role.query.all()]

class ReviewForm(FlaskForm):
    rating = SelectField('Оценка', choices=[
        (5, 'Отлично'),
        (4, 'Хорошо'),
        (3, 'Удовлетворительно'),
        (2, 'Неудовлетворительно'),
        (1, 'Плохо'),
        (0, 'Ужасно')
    ], coerce=int, validators=[DataRequired()])
    text = TextAreaField('Текст рецензии', validators=[DataRequired()])
    submit = SubmitField('Сохранить')
