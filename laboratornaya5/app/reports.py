import io
from flask import Blueprint, redirect, render_template, request, send_file, flash
from app import db_connector
from mysql.connector.errors import DatabaseError
import csv

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')

@reports_bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    logs = []
    total_logs = 0

    try:
        db_connection = db_connector.connect()
        with db_connection.cursor(named_tuple=True) as cursor:
            cursor.execute("SELECT COUNT(*) AS count FROM visit_logs")
            total_logs = cursor.fetchone().count
            offset = (page - 1) * per_page
            query = ("SELECT visit_logs.id, users.login, visit_logs.path, visit_logs.created_at "
                     "FROM visit_logs LEFT JOIN users ON visit_logs.user_id = users.id "
                     "ORDER BY visit_logs.created_at DESC "
                     "LIMIT %s OFFSET %s")
            cursor.execute(query, (per_page, offset))
            logs = cursor.fetchall()
    except DatabaseError as error:
        print(f"Database error occurred: {error}")
        flash(f"Произошла ошибка при получении данных журнала посещений: {error}", "danger")
        return render_template('visit_logs.html', logs=[], page=page, per_page=per_page, total_logs=total_logs)
    finally:
        db_connection.close()

    return render_template('visit_logs.html', logs=logs, page=page, per_page=per_page, total_logs=total_logs)

@reports_bp.route('/users_stat')
def users_stat():
    logs = []
    try:
        db_connection = db_connector.connect()
        with db_connection.cursor(named_tuple=True) as cursor:
            query = ("SELECT users.login, COUNT(*) as visit_count "
                     "FROM visit_logs LEFT JOIN users on visit_logs.user_id = users.id "
                     "GROUP BY users.id "
                     "ORDER BY visit_count desc;")
            cursor.execute(query)
            logs = cursor.fetchall()
            return render_template("users_stat.html", logs=logs)
    except DatabaseError as error:
        print(f"Произошла ошибка БД: {error}")
        return render_template("users_stat.html", logs=logs)
    finally:
        db_connection.close()

@reports_bp.route('/pages_stat')
def pages_stat():
    pages = []
    try:
        db_connection = db_connector.connect()
        with db_connection.cursor(named_tuple=True) as cursor:
            query = ("SELECT path, COUNT(*) as visit_count FROM visit_logs GROUP BY path ORDER BY visit_count DESC")
            cursor.execute(query)
            pages = cursor.fetchall()
    except DatabaseError as error:
        print(f"Database error occurred: {error}")
        flash(f"Произошла ошибка при получении данных отчёта по страницам: {error}", "danger")
        return render_template('pages_report.html', pages=[])
    finally:
        db_connection.close()

    return render_template('pages_report.html', pages=pages)

@reports_bp.route('/pages_report_csv')
def pages_report_csv():
    try:
        db_connection = db_connector.connect()
        with db_connection.cursor(named_tuple=True) as cursor:
            query = ("SELECT path, COUNT(*) as visit_count FROM visit_logs GROUP BY path ORDER BY visit_count DESC")
            cursor.execute(query)
            rows = cursor.fetchall()

            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(['Path', 'Visit Count'])
            for row in rows:
                writer.writerow([row.path, row.visit_count])
            output.seek(0)
            
            return send_file(io.BytesIO(output.getvalue().encode()), mimetype='text/csv', download_name='pages_report.csv', as_attachment=True)
    except DatabaseError as error:
        print(f"Database error occurred: {error}")
        flash(f"Произошла ошибка при экспорте данных отчёта по страницам: {error}", "danger")
        return redirect(request.referrer)
    finally:
        db_connection.close()

@reports_bp.route('/users_report')
def users_report():
    users = []
    try:
        db_connection = db_connector.connect()
        with db_connection.cursor(named_tuple=True) as cursor:
            query = ("SELECT users.login, COUNT(*) as visit_count "
                     "FROM visit_logs LEFT JOIN users ON visit_logs.user_id = users.id "
                     "GROUP BY users.id "
                     "ORDER BY visit_count DESC")
            cursor.execute(query)
            users = cursor.fetchall()
    except DatabaseError as error:
        print(f"Database error occurred: {error}")
        flash(f"Произошла ошибка при получении данных отчёта по пользователям: {error}", "danger")
        return render_template('users_report.html', users=[])
    finally:
        db_connection.close()

    return render_template('users_report.html', users=users)

@reports_bp.route('/users_report.csv')
def users_report_csv():
    try:
        db_connection = db_connector.connect()
        with db_connection.cursor(named_tuple=True) as cursor:
            query = ("SELECT users.login, COUNT(*) as visit_count "
                     "FROM visit_logs LEFT JOIN users ON visit_logs.user_id = users.id "
                     "GROUP BY users.id "
                     "ORDER BY visit_count DESC")
            cursor.execute(query)
            rows = cursor.fetchall()

            output = io.BytesIO()
            writer = csv.writer(output)
            writer.writerow(['User', 'Visit Count'])
            for row in rows:
                writer.writerow([row.login, row.visit_count])
            output.seek(0)

            return send_file(output, mimetype='text/csv', download_name='users_report.csv', as_attachment=True)
    except DatabaseError as error:
        print(f"Database error occurred: {error}")
        flash(f"Произошла ошибка при экспорте данных отчёта по пользователям: {error}", "danger")
        return redirect(request.referrer)
    finally:
        db_connection.close()