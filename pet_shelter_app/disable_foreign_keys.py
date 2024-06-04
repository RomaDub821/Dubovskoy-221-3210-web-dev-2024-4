from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    connection = db.engine.connect()
    
    # Отключение проверок внешних ключей
    connection.execute(text('SET FOREIGN_KEY_CHECKS = 0'))
    
    # Удаление таблицы roles (если она существует)
    connection.execute(text('DROP TABLE IF EXISTS roles'))

    # Выполнение миграций
    from flask_migrate import upgrade
    upgrade()

    # Включение проверок внешних ключей
    connection.execute(text('SET FOREIGN_KEY_CHECKS = 1'))
    
    # Закрытие соединения
    connection.close()
