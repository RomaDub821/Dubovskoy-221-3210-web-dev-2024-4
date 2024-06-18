from flask import render_template, redirect, send_from_directory, url_for, flash, request, current_app
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from app import app, db
from app.forms import BookForm, LoginForm, RegistrationForm, ReviewForm
from app.models import Book, Cover, Genre, Review, User, Role
import os
import hashlib
import bleach

@app.template_filter('genres_list')
def genres_list(genres):
    return ', '.join([genre.name for genre in genres])

@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    books = Book.query.order_by(Book.year.desc()).paginate(page=page, per_page=10)
    return render_template('index.html', books=books)

@app.route('/book/add', methods=['GET', 'POST'])
@login_required
def book_add():
    form = BookForm()
    if form.validate_on_submit():
        app.logger.info('Форма добавления книги прошла валидацию.')
        try:
            cover = None
            if form.cover.data:
                filename = secure_filename(form.cover.data.filename)
                mimetype = form.cover.data.mimetype
                md5_hash = hashlib.md5(form.cover.data.read()).hexdigest()
                existing_cover = Cover.query.filter_by(md5_hash=md5_hash).first()
                if existing_cover:
                    cover = existing_cover
                else:
                    cover = Cover(filename=filename, mime_type=mimetype, md5_hash=md5_hash)
                    db.session.add(cover)
                    db.session.commit()
                    form.cover.data.seek(0)
                    form.cover.data.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                app.logger.info(f'Обложка книги сохранена: {filename}')

            description_sanitized = bleach.clean(form.description.data)
            book = Book(title=form.title.data, description=description_sanitized, year=form.year.data,
                        publisher=form.publisher.data, author=form.author.data, pages=form.pages.data,
                        cover_id=cover.id if cover else None)
            book.genres = [Genre.query.get(id) for id in form.genres.data]
            db.session.add(book)
            db.session.commit()
            flash('Книга добавлена', 'success')
            app.logger.info(f'Книга {form.title.data} добавлена в базу данных.')
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            flash('Ошибка при добавлении книги. Попробуйте еще раз.', 'danger')
            app.logger.error(f'Ошибка при добавлении книги: {e}')
    return render_template('books.html', form=form)

@app.route('/book/<int:book_id>')
def book_view(book_id):
    book = Book.query.get_or_404(book_id)
    user_has_reviewed = any(review.user_id == current_user.id for review in book.reviews) if current_user.is_authenticated else False
    return render_template('books_info.html', book=book, user_has_reviewed=user_has_reviewed)

@app.route('/book/edit/<int:book_id>', methods=['GET', 'POST'])
@login_required
def book_edit(book_id):
    book = Book.query.get_or_404(book_id)
    form = BookForm(obj=book)
    if form.validate_on_submit():
        try:
            book.title = form.title.data
            book.description = form.description.data
            book.year = form.year.data
            book.publisher = form.publisher.data
            book.author = form.author.data
            book.pages = form.pages.data
            book.genres = [Genre.query.get(id) for id in form.genres.data]
            db.session.commit()
            flash('Книга обновлена', 'success')
            app.logger.info(f'Книга с ID {book_id} обновлена.')
            return redirect(url_for('book_view', book_id=book.id))
        except Exception as e:
            db.session.rollback()
            flash('Ошибка при обновлении книги. Попробуйте еще раз.', 'danger')
            app.logger.error(f'Ошибка при обновлении книги: {e}')
    return render_template('books.html', form=form)

@app.route('/book/delete/<int:book_id>', methods=['POST'])
@login_required
def book_delete(book_id):
    try:
        book = Book.query.get_or_404(book_id)
        if book.cover:
            cover_path = os.path.join(app.config['UPLOAD_FOLDER'], book.cover.filename)
            if os.path.exists(cover_path):
                os.remove(cover_path)
                app.logger.info(f'Обложка книги удалена: {book.cover.filename}')
        db.session.delete(book)
        db.session.commit()
        flash('Книга удалена', 'success')
        app.logger.info(f'Книга с ID {book_id} удалена.')
        return redirect(url_for('index'))
    except Exception as e:
        db.session.rollback()
        flash('Ошибка при удалении книги. Попробуйте еще раз.', 'danger')
        app.logger.error(f'Ошибка при удалении книги: {e}')
        return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember_me.data)
            app.logger.info(f'Пользователь {user.username} вошел в систему.')
            return redirect(url_for('index'))
        else:
            flash('Неверный логин или пароль', 'danger')
            app.logger.warning(f'Неудачная попытка входа для пользователя {form.username.data}.')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    if current_user.is_authenticated:
        app.logger.info(f'Пользователь {current_user.username} вышел из системы.')
        logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
            user = User(username=form.username.data, password_hash=hashed_password,
                        surname=form.surname.data, name=form.name.data, patronymic=form.patronymic.data,
                        role_id=form.role.data)
            db.session.add(user)
            db.session.commit()
            flash('Вы успешно зарегистрировались! Теперь вы можете войти.', 'success')
            app.logger.info(f'Новый пользователь зарегистрирован: {form.username.data}.')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('Ошибка при регистрации. Попробуйте еще раз.', 'danger')
            app.logger.error(f'Ошибка при регистрации: {e}')
    return render_template('register.html', form=form)

@app.route('/book/<int:book_id>/review/add', methods=['GET', 'POST'])
@login_required
def add_review(book_id):
    book = Book.query.get_or_404(book_id)
    form = ReviewForm()
    if form.validate_on_submit():
        try:
            review = Review(
                rating=form.rating.data,
                text=bleach.clean(form.text.data),
                user_id=current_user.id,
                book_id=book_id
            )
            db.session.add(review)
            db.session.commit()
            flash('Рецензия добавлена', 'success')
            app.logger.info(f'Рецензия добавлена для книги с ID {book_id} пользователем {current_user.username}.')
            return redirect(url_for('book_view', book_id=book_id))
        except Exception as e:
            db.session.rollback()
            flash('Ошибка при добавлении рецензии. Попробуйте еще раз.', 'danger')
            app.logger.error(f'Ошибка при добавлении рецензии: {e}')
    return render_template('add_review.html', form=form, book=book)


def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(f"Ошибка в поле {getattr(form, field).label.text}: {error}", 'danger')
            app.logger.warning(f"Ошибка в поле {getattr(form, field).label.text}: {error}")

