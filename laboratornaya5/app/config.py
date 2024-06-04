import os
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY')

MYSQL_USER = os.getenv('MYSQL_USER', 'std_2407_lab')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'Duba13579')
MYSQL_HOST = os.getenv('MYSQL_HOST', 'std-mysql.ist.mospolytech.ru')
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'std_2407_lab')
ADMIN_ROLE_ID = 3