from flask import Flask, flash, render_template, request, redirect, session, url_for
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user
import config

app = Flask(__name__)
app.config.from_object(config)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login" ##
login_manager.login_message = "Войдите, чтобы просматривать содержимое данной страницы"
login_manager.login_message_category = "warning"

class User(UserMixin): ## почему mixin и декоратор
    def __init__(self, user_id, login):
        self.id = user_id
        self.login = login

def get_user_list():
    return [{"user_id": "1", "login": "user", "password": "qwerty"}, {"user_id": "2", "login": "admin", "password": "admin"},]

@login_manager.user_loader  
def load_user(user_id): 
    for user_entry in get_user_list():
        if user_id == user_entry["user_id"]:
            return User(user_id, user_entry["login"])
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
    for user in get_user_list():
        if login == user["login"] and password == user["password"]:
            login_user(User(user["user_id"], user["login"]), remember=remember) ## 
            flash("Успешная авторизация", category="success") ## где 
            target_page = request.args.get("next", url_for("index"))
            return redirect(target_page)

    flash("Введены некорректные учётные данные пользователя", category="danger")    
    return render_template("login.html")

@app.route('/logout')
def logout():
    logout_user() ## 
    return redirect(url_for("index"))

@app.route('/secret')
@login_required
def secret():
    return render_template("secret.html")

@app.route('/views_count')
def views_count():
    session['visit_count'] = session.get('visit_count', 0) + 1
    return render_template('views_count.html', visit_count=session['visit_count'])

## load_user в какой момент и зачем декоратор конкретно
## класс юзер какие требования и почему миксим
##login_user logout_user
## flash где хранится сообщение между запросами
## атрибуты логин вью логин мэссэдж и логин мэсседж кэтигори