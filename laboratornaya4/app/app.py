from flask import Flask, flash, render_template, request, redirect, session, url_for
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from mysqldb import DBConnector
from mysql.connector.errors import DatabaseError
import config

app = Flask(__name__)
app.config.from_object(config)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = "Войдите, чтобы просматривать содержимое данной страницы"
login_manager.login_message_category = "warning"

db_connector = DBConnector(app)

class User(UserMixin):
    def __init__(self, user_id, login):
        self.id = user_id
        self.login = login

def validate_password(password):
    errors = []
    
    if not (8 <= len(password) <= 128):
        errors.append("Пароль должен содержать от 8 до 128 символов")
    if not any(char.isupper() for char in password):
        errors.append("Пароль должен содержать как минимум одну заглавную букву")
    if not any(char.islower() for char in password):
        errors.append("Пароль должен содержать как минимум одну строчную букву")
    if not any(char.isdigit() for char in password):
        errors.append("Пароль должен содержать как минимум одну цифру")
    if ' ' in password:
        errors.append("Пароль не должен содержать пробелы")
    allowed_symbols = r"~!?\@#\$%\^&\*_\-\+\(\)\[\]\{\}<>\\/\"'\.,:;"
    if not all(char.isalnum() or char in allowed_symbols for char in password):
        errors.append("Пароль может содержать только латинские или кириллические буквы, цифры "
                      "и следующие символы: ~ ! ? @ # $ % ^ & * _ - + ( ) [ ] { } > < / \\ | \" ' . , : ;")
    return errors

def validate_user_data(user_data):
    errors = {}
    required_fields = ['login', 'password', 'last_name', 'first_name']
    for field in required_fields:
        if not user_data.get(field):
            errors[field] = "Это поле не может быть пустым"
    if len(user_data.get('login', '')) < 5:
        errors['login'] = "Логин должен содержать не менее 5 символов"
    password_errors = validate_password(user_data.get('password', ''))
    if password_errors:
        errors['password'] = ", ".join(password_errors)
    return errors

def get_roles():
    query = "SELECT * FROM roles"

    with db_connector.connect().cursor(named_tuple=True) as cursor:
        cursor.execute(query)
        roles = cursor.fetchall()
    return roles

def get_user_list():
    return [{"user_id": "1", "login": "user", "password": "qwerty"}, {"user_id": "2", "login": "admin", "password": "admin"},]

CREATE_USER_FIELDS = ['login', 'password', 'last_name', 'first_name', 'middle_name', 'role_id']
EDIT_USER_FIELDS = ['last_name', 'first_name', 'middle_name', 'role_id']

@login_manager.user_loader
def load_user(user_id):
    query = "SELECT id, login FROM users WHERE id=%s"

    with db_connector.connect().cursor(named_tuple=True) as cursor:

        cursor.execute(query, (user_id,))
        
        user = cursor.fetchone()

    if user:
        return User(user_id, user.login)
    
    return None

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("login.html")

    login = request.form.get("login", "")
    password = request.form.get("password", "")
    remember = request.form.get("remember") == "on"
    query = 'SELECT id, login FROM users WHERE login=%s AND password_hash=SHA2(%s, 256)'

    print(query)

    with db_connector.connect().cursor(named_tuple=True) as cursor:

        cursor.execute(query, (login, password))

        print(cursor.statement)

        user = cursor.fetchone()

    if user:
        login_user(User(user.id, user.login), remember=remember)
        flash("Успешная авторизация", category="success")
        target_page = request.args.get("next", url_for("index"))
        return redirect(target_page)

    flash("Введены некорректные учётные данные пользователя", category="danger")   
   
    return render_template("login.html")

@app.route('/users')
def users():
    query = 'SELECT users.*, roles.name as role_name FROM users LEFT JOIN roles ON users.role_id = roles.id'

    with db_connector.connect().cursor(named_tuple=True) as cursor:
        cursor.execute(query)
        data = cursor.fetchall() 

    return render_template("users.html", users=data)

def get_form_data(required_fields):
    user = {}

    for field in required_fields:
        user[field] = request.form.get(field) or None

    return user

@app.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    query = ("SELECT * FROM users where id = %s")
    roles = get_roles()
    with db_connector.connect().cursor(named_tuple=True) as cursor:
        cursor.execute(query, (user_id, ))
        user = cursor.fetchone()

    if request.method == "POST":
        user = get_form_data(EDIT_USER_FIELDS)
        user['user_id'] = user_id
        query = ("UPDATE users "
                 "SET last_name=%(last_name)s, first_name=%(first_name)s, "
                 "middle_name=%(middle_name)s, role_id=%(role_id)s "
                 "WHERE id=%(user_id)s ")

        try:
            with db_connector.connect().cursor(named_tuple=True) as cursor:
                cursor.execute(query, user)
                db_connector.connect().commit()
            
            flash("Запись пользователя успешно обновлена", category="success")
            return redirect(url_for('users'))
        except DatabaseError as error:
            flash(f'Ошибка редактирования пользователя! {error}', category="danger")
            db_connector.connect().rollback()    

    return render_template("edit_user.html", user=user, roles=roles)

@app.route('/user/<int:user_id>/delete', methods=["POST"])
@login_required
def delete_user(user_id):
    query = "DELETE FROM users WHERE id=%s"

    try:
        with db_connector.connect().cursor(named_tuple=True) as cursor:
            cursor.execute(query, (user_id, ))
            db_connector.connect().commit() 
        
        flash("Запись пользователя успешно удалена", category="success")
    except DatabaseError as error:
        flash(f'Ошибка удаления пользователя! {error}', category="danger")
        db_connector.connect().rollback()    
    
    return redirect(url_for('users'))

@app.route('/users/new', methods=['GET', 'POST'])
@login_required
def create_user():
    errors = {}
    user = {}
    roles = get_roles()
    if request.method == 'POST':
        user = get_form_data(CREATE_USER_FIELDS)
        errors = validate_user_data(user)
        if not errors:
            query = ("INSERT INTO users "
                     "(login, password_hash, last_name, first_name, middle_name, role_id) "
                     "VALUES (%(login)s, SHA2(%(password)s, 256), "
                     "%(last_name)s, %(first_name)s, %(middle_name)s, %(role_id)s)")
            try:
                with db_connector.connect().cursor(named_tuple=True) as cursor:
                    cursor.execute(query, user)
                    db_connector.connect().commit()
                return redirect(url_for('users'))
            except DatabaseError as error:
                flash(f'Ошибка создания пользователя! {error}', category="danger")    
                db_connector.connect().rollback()

    return render_template("user_form.html", user=user, roles=roles, errors=errors)


@app.route('/users/<int:user_id>')
def view_user(user_id):
    query = """
        SELECT users.id, users.login, users.last_name, users.first_name, 
               users.middle_name, roles.name as role_name 
        FROM users 
        LEFT JOIN roles ON users.role_id = roles.id 
        WHERE users.id=%s
    """
    with db_connector.connect().cursor(named_tuple=True) as cursor:
        cursor.execute(query, (user_id,))
        user = cursor.fetchone()
    return render_template('view_user.html', user=user)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for("index"))

@app.route('/secret')
@login_required
def secret():
    return render_template("secret.html")

@app.route('/views_count')
def views_count():
    session['visit_count'] = session.get('visit_count', 0) + 1
    return render_template('views_count.html', visit_count=session['visit_count'])

# python -m venv ve
# . ve/bin/activate -- Linux
# ve\Scripts\activate -- Windows
# pip install flask python-dotenv