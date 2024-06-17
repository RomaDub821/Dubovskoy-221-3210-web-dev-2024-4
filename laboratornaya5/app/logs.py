from flask import Blueprint, render_template, request, flash
from flask_login import current_user, login_required
from app import db_connector
from mysql.connector.errors import DatabaseError
import math

logs_bp = Blueprint('logs', __name__, url_prefix='/logs')

@logs_bp.route('/')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    logs = []
    total_logs = 0
    total_pages = 1

    try:
        db_connection = db_connector.connect()
        cursor = db_connection.cursor(named_tuple=True)

        if current_user.is_admin():
            cursor.execute("SELECT COUNT(*) AS count FROM visit_logs")
        else:
            cursor.execute("SELECT COUNT(*) AS count FROM visit_logs WHERE user_id = %s", (current_user.id,))
        total_logs = cursor.fetchone().count

        offset = (page - 1) * per_page

        if current_user.is_admin():
            query = ("SELECT visit_logs.id, users.login, visit_logs.path, visit_logs.created_at "
                     "FROM visit_logs LEFT JOIN users ON visit_logs.user_id = users.id "
                     "ORDER BY visit_logs.created_at DESC "
                     "LIMIT %s OFFSET %s")
            cursor.execute(query, (per_page, offset))
        else:
            query = ("SELECT visit_logs.id, users.login, visit_logs.path, visit_logs.created_at "
                     "FROM visit_logs LEFT JOIN users ON visit_logs.user_id = users.id "
                     "WHERE visit_logs.user_id = %s "
                     "ORDER BY visit_logs.created_at DESC "
                     "LIMIT %s OFFSET %s")
            cursor.execute(query, (current_user.id, per_page, offset))

        logs = cursor.fetchall()
        print(f"Fetched logs: {logs}")

        cursor.close()
    except DatabaseError as error:
        print(f"Database error occurred: {error}")
        flash(f"Произошла ошибка при получении данных журнала посещений: {error}", "danger")
        return render_template('visit_logs.html', logs=[], page=page, per_page=per_page, total_logs=total_logs)
    finally:
        db_connection.close()

    if total_logs > 0:
        total_pages = math.ceil(total_logs / per_page)

    return render_template('visit_logs.html', logs=logs, page=page, per_page=per_page, total_logs=total_logs, total_pages=total_pages)
