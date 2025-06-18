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


# Получить список всех категорий из БД
def get_categories():
    cats = query_db("SELECT id, name FROM categories ORDER BY name")
    return [dict(row) for row in cats]


# Получить список блюд (можно фильтровать по категории)
def get_dishes(category_id=None):
    if category_id:
        dishes = query_db("SELECT * FROM dishes WHERE category_id=? ORDER BY id DESC", (category_id,))
    else:
        dishes = query_db("SELECT * FROM dishes ORDER BY id DESC")
    return [dict(row) for row in dishes]


# Получить одно блюдо по его id
def get_dish_by_id(dish_id):
    row = query_db("SELECT * FROM dishes WHERE id=?", (dish_id,), one=True)
    return dict(row) if row else None


# Зарегистрировать пользователя, если email ещё не занят
def register_user(email, name, password):
    if query_db("SELECT id FROM users WHERE email=?", (email,), one=True):
        return False
    execute_db("INSERT INTO users (email, name, password, is_admin) VALUES (?, ?, ?, 0)", (email, name, password))
    return True


# Проверить логин и пароль пользователя
def login_user(email, password):
    print(f"Попытка входа: email={email}, password={password}")
    row = query_db("SELECT id, name, is_admin FROM users WHERE email=? AND password=?", (email, password), one=True)
    if row:
        print(f"Пользователь найден: {row['name']}")
        return {"id": row["id"], "name": row["name"], "is_admin": bool(row["is_admin"])}
    print("Пользователь не найден или пароль неверный")
    return None


# Получить список заказов для пользователя (или всех, если user_id не задан)
def get_orders(user_id=None):
    if user_id:
        orders = query_db("SELECT * FROM orders WHERE user_id=? ORDER BY created_at DESC", (user_id,))
    else:
        orders = query_db("SELECT * FROM orders ORDER BY created_at DESC")
    return [dict(row) for row in orders]


# Получить заказы с именем пользователя (для админки)
def get_orders_manage_orders(user_id=None):
    if user_id:
        orders = query_db("""
        SELECT orders.*, users.name AS user_name
        FROM orders
        JOIN users ON orders.user_id = users.id
        WHERE user_id=?
        ORDER BY orders.created_at DESC
    """, (user_id,))
    else:
        orders = query_db("""
        SELECT orders.*, users.name AS user_name
        FROM orders
        JOIN users ON orders.user_id = users.id
        ORDER BY orders.created_at DESC
    """)
    return [dict(row) for row in orders]


# Оформить заказ: добавить запись в orders и order_items
def place_order(user_id, items, address, phone, delivery_time, payment_method):
    order_id = execute_db(
        "INSERT INTO orders (user_id, address, phone, status, created_at, payment_method, delivery_time) VALUES (?, ?, ?, ?, datetime('now'), ?, ?)",
        (user_id, address, phone, "Принят", payment_method, delivery_time))
    for dish_id, qty in items.items():
        execute_db("INSERT INTO order_items (order_id, dish_id, qty) VALUES (?, ?, ?)", (order_id, dish_id, qty))
    return order_id

# Добавить отзыв к блюду
def add_review(user_id, dish_id, rating, text):
    execute_db("INSERT INTO reviews (user_id, dish_id, rating, text, created_at) VALUES (?, ?, ?, ?, datetime('now'))",
              (user_id, dish_id, rating, text))
    

# Получить все отзывы к блюду
def get_reviews_for_dish(dish_id):
    reviews = query_db(
        "SELECT r.rating, r.text, u.name, r.created_at FROM reviews r JOIN users u ON r.user_id = u.id WHERE r.dish_id=? ORDER BY r.created_at DESC",
        (dish_id,))
    return [dict(row) for row in reviews]


# Декоратор: требовать логин пользователя для доступа
def login_required(f):
    def wrap(*args, **kwargs):
        if not session.get("user_id"):
            return redirect(url_for('login_register_combined'))
        return f(*args, **kwargs)
    wrap.__name__ = f.__name__
    return wrap


# Декоратор: требовать права админа для доступа
def admin_required(f):
    def wrap(*args, **kwargs):
        if not session.get("is_admin"):
            flash("Только для админа!")
            return redirect(url_for('login_register_combined'))
        return f(*args, **kwargs)
    wrap.__name__ = f.__name__
    return wrap
