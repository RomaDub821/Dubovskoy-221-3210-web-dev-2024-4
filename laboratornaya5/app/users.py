from flask import render_template, request, redirect, url_for, flash, Blueprint
from flask_login import login_required, current_user
from mysql.connector.errors import DatabaseError
from app import db_connector
from authorization import can_user

bp = Blueprint('users', __name__, url_prefix='/users')

CREATE_USER_FIELDS = ['login', 'password', 'last_name', 'first_name', 'middle_name', 'role_id']
EDIT_USER_FIELDS = ['last_name', 'first_name', 'middle_name', 'role_id']

def get_roles():
    query = "SELECT * FROM roles"

    with db_connector.connect().cursor(named_tuple=True) as cursor:
        cursor.execute(query)
        roles = cursor.fetchall()
    return roles

@bp.route('/')
def index():
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

@bp.route('/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@can_user('edit')
def edit(user_id):
    query = ("SELECT * FROM users where id = %s")
    roles = get_roles()
    with db_connector.connect().cursor(named_tuple=True) as cursor:
        cursor.execute(query, (user_id, ))
        user = cursor.fetchone()

    if request.method == "POST":
        user = get_form_data(EDIT_USER_FIELDS)
        if not current_user.can('assign_roles'):
            del user['role_id']

        columns = ','.join([f'{key}=%({key})s' for key in user])
        user['user_id'] = user_id
        query = (f"UPDATE users SET {columns} WHERE id=%(user_id)s ")

        try:
            with db_connector.connect().cursor(named_tuple=True) as cursor:
                cursor.execute(query, user)
                print(cursor.statement)
                db_connector.connect().commit()
            
            flash("Запись пользователя успешно обновлена", category="success")
            return redirect(url_for('users.index'))
        except DatabaseError as error:
            flash(f'Ошибка редактирования пользователя! {error}', category="danger")
            db_connector.connect().rollback()    

    return render_template("edit_user.html", user=user, roles=roles)

@bp.route('/<int:user_id>/delete', methods=["POST"])
@login_required
@can_user('delete')
def delete(user_id):
    query = "DELETE FROM users WHERE id=%s"

    try:
        with db_connector.connect().cursor(named_tuple=True) as cursor:
            cursor.execute(query, (user_id, ))
            db_connector.connect().commit() 
        
        flash("Запись пользователя успешно удалена", category="success")
    except DatabaseError as error:
        flash(f'Ошибка удаления пользователя! {error}', category="danger")
        db_connector.connect().rollback()    
    
    return redirect(url_for('users.index'))

@bp.route('/new', methods=['GET', 'POST'])
@login_required
@can_user('create')
def create():
    user = {}
    roles = get_roles()
    if request.method == 'POST':
        user = get_form_data(CREATE_USER_FIELDS)

        query = ("INSERT INTO users "
                 "(login, password_hash, last_name, first_name, middle_name, role_id) "
                 "VALUES (%(login)s, SHA2(%(password)s, 256), "
                 "%(last_name)s, %(first_name)s, %(middle_name)s, %(role_id)s)")
        try:
            with db_connector.connect().cursor(named_tuple=True) as cursor:
                cursor.execute(query, user)
                db_connector.connect().commit()
            return redirect(url_for('users.index'))
        except DatabaseError as error:
            flash(f'Ошибка создания пользователя! {error}', category="danger")    
            db_connector.connect().rollback()

    return render_template("user_form.html", user=user, roles=roles)