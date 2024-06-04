import math
from flask import Blueprint, render_template, request, flash
from app import db_connector
from mysql.connector.errors import DatabaseError

logs_bp = Blueprint('logs', __name__, url_prefix='/logs')

@logs_bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    logs = []
    total_logs = 0
    total_pages = 1  # Ensure total_pages is always defined

    try:
        db_connection = db_connector.connect()
        with db_connection.cursor(named_tuple=True) as cursor:
            cursor.execute("SELECT COUNT(*) AS count FROM visit_logs")
            result = cursor.fetchone()
            total_logs = result.count if result else 0  # Ensure total_logs is assigned correctly

            offset = (page - 1) * per_page
            query = ("SELECT visit_logs.id, users.login, visit_logs.path, visit_logs.created_at "
                     "FROM visit_logs LEFT JOIN users ON visit_logs.user_id = users.id "
                     "ORDER BY visit_logs.created_at DESC "
                     "LIMIT %s OFFSET %s")
            cursor.execute(query, (per_page, offset))
            logs = cursor.fetchall()
            print(f"Fetched logs: {logs}")  # Debugging line to see fetched logs
    except DatabaseError as error:
        print(f"Database error occurred: {error}")
        flash(f"Произошла ошибка при получении данных журнала посещений: {error}", "danger")
    finally:
        if db_connection.is_connected():
            db_connection.close()  # Ensure the connection is closed

    total_pages = math.ceil(total_logs / per_page)

    return render_template('visit_logs.html', logs=logs, page=page, per_page=per_page, total_logs=total_logs, total_pages=total_pages)
