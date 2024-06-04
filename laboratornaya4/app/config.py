import os
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY')

#SECRET_KEY= '5l2qi0sdi3xu44rp61or1f0lv7hhm5w2d7z5bgvb60vuq68vlxxrw4kkbryhffza'
# SECRET_KEY = os.environ.get('SECRET_KEY')

MYSQL_USER = "std_2407_lab"
MYSQL_DATABASE = "std_2407_lab"
MYSQL_PASSWORD = "Duba13579"
MYSQL_HOST = "std-mysql.ist.mospolytech.ru"