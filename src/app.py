import os  # Работа с файловой системой и путями

# Импорт нужных функций и классов из flask
from flask import (
    Flask,               # Основной класс приложения Flask
    render_template,     # Для рендера html-шаблонов
    request,             # Для доступа к данным запроса (POST, GET)
    redirect,            # Для редиректов между страницами
    url_for,             # Для генерации url по имени функции
    session,             # Для работы с пользовательской сессией
    flash,               # Для всплывающих сообщений
    send_from_directory, # Для отдачи файлов из папки (например, изображений)
    g                   # Глобальный объект для хранения данных на время запроса
)
from werkzeug.utils import secure_filename  # Для защиты имён загружаемых файлов

# Импорт функций для работы с БД из модуля database.py
from database import get_db, close_db, init_db, query_db, execute_db

# Создание экземпляра Flask-приложения, указываем папки для шаблонов и статики
app = Flask(__name__, template_folder='templates', static_folder='static')
app.config["SECRET_KEY"] = "pizza17secret"  # Секретный ключ для хранения сессий и защиты от подделки cookie
app.config["UPLOAD_FOLDER"] = os.path.join("static", "uploads")  # Путь к папке для загрузки файлов
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)  # Создать папку uploads, если её нет



# Перед каждым запросом подключаемся к базе данных
@app.before_request
def before_request():
    get_db()


# После каждого запроса закрываем соединение с БД
@app.teardown_appcontext
def teardown_db(exception):
    close_db()


# Команда CLI для инициализации базы данных — можно вызвать командой flask init-db
@app.cli.command("init-db")
def initdb_command():
    """Инициализация базы данных из schema.sql"""
    init_db()
    print("База данных инициализирована.")