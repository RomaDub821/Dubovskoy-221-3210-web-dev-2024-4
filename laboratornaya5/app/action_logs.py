from flask import Blueprint,  render_template
from app import db_connector
from mysql.connector.errors import DatabaseError

logs_bp = Blueprint('logs', __name__, url_prefix='/logs')

@logs_bp.route('/')
def index():
    logs = []
    try:
        db_connection = db_connector.connect()
        with db_connection.cursor(named_tuple=True) as cursor:
            query = ("SELECT action_logs.id, users.login, action_logs.path, action_logs.created_at "
                     "FROM action_logs LEFT JOIN users ON action_logs.user_id = users.id")
            cursor.execute(query)
            logs = cursor.fetchall()

            return render_template("action_logs.html", logs=logs)
    except DatabaseError as error:
        print(f"Произошла ошибка БД: {error}")

@logs_bp.route('/users_stat')
def users_stat():
    logs = []    
    try:
        db_connection = db_connector.connect()
        with db_connection.cursor(named_tuple=True) as cursor:
            query = ("SELECT users.login, COUNT(*) as visit_count "
            "FROM action_logs LEFT JOIN users on action_logs.user_id = users.id "
            "GROUP BY users.id "
            "ORDER BY visit_count desc;")
            cursor.execute(query)
            logs = cursor.fetchall()
            return render_template("users_stat.html", logs=logs)
    except DatabaseError as error:
        print(f"Произошла ошибка БД: {error}")    

@logs_bp.route('/pagess_stat')
def pages_stat():
    return render_template("logs_base.html")