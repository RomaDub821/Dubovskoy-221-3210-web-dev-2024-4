from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, SelectMultipleField, FileField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Length
from app.models import Genre

class BookForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Краткое описание', validators=[DataRequired()])
    year = IntegerField('Год', validators=[DataRequired()])
    publisher = StringField('Издательство', validators=[DataRequired(), Length(max=100)])
    author = StringField('Автор', validators=[DataRequired(), Length(max=100)])
    pages = IntegerField('Объём (в страницах)', validators=[DataRequired()])
    genres = SelectMultipleField('Жанры', coerce=int)
    cover = FileField('Обложка')

    def __init__(self, *args, **kwargs):
        super(BookForm, self).__init__(*args, **kwargs)
        self.genres.choices = [(genre.id, genre.name) for genre in Genre.query.all()]

class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
