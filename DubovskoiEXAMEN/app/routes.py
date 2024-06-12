from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, db
from app.forms import BookForm, LoginForm
from app.models import Book, Cover, Genre, Review, User, Role
import os
import hashlib
from werkzeug.utils import secure_filename

@app.route('/')
def index():
    books = Book.query.all()
    return render_template('index.html', books=books)

@app.route('/book/add', methods=['GET', 'POST'])
@login_required
def book_add():
    form = BookForm()
    if form.validate_on_submit():
        cover = None
        if form.cover.data:
            filename = secure_filename(form.cover.data.filename)
            mimetype = form.cover.data.mimetype
            md5_hash = hashlib.md5(form.cover.data.read()).hexdigest()
            cover = Cover(filename=filename, mime_type=mimetype, md5_hash=md5_hash)
            db.session.add(cover)
            db.session.commit()
            form.cover.data.seek(0)
            form.cover.data.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        book = Book(title=form.title.data, description=form.description.data, year=form.year.data,
                    publisher=form.publisher.data, author=form.author.data, pages=form.pages.data,
                    cover_id=cover.id if cover else None)
        db.session.add(book)
        db.session.commit()
        flash('Книга добавлена', 'success')
        return redirect(url_for('index'))
    return render_template('books.html', form=form)

@app.route('/book/<int:book_id>')
def book_view(book_id):
    book = Book.query.get_or_404(book_id)
    return render_template('books_info.html', book=book)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect(url_for('index'))
        else:
            flash('Неверный логин или пароль', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))
