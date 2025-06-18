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


# ---------------------- МАРШРУТЫ ПОЛЬЗОВАТЕЛЯ ----------------------

# Логин и регистрация (одна форма)
@app.route("/login", methods=["GET", "POST"])
def login_register_combined():
    if request.method == "POST":
        action = request.form.get("form_type")  # login или register
        email = request.form.get("email")
        password = request.form.get("password")

        if action == "login":
            user = login_user(email, password)
            if user:
                session["user_id"] = user["id"]
                session["user_name"] = user["name"]
                session["is_admin"] = user["is_admin"]
                return redirect(url_for("index"))
            else:
                flash("Неверная почта или пароль!")
                return redirect(url_for("login_register_combined"))

        elif action == "register":
            name = request.form.get("name")
            if not (email and name and password):
                flash("Заполните все поля для регистрации!")
                return redirect(url_for("login_register_combined"))
            elif register_user(email, name, password):
                flash("Регистрация успешна, войдите!")
                return redirect(url_for("login_register_combined"))
            else:
                flash("Пользователь с такой почтой уже есть!")
                return redirect(url_for("login_register_combined"))

    return render_template("login.html")


# Выход из аккаунта: очищаем сессию
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


# Главная страница: категории и блюда
@app.route("/")
def index():
    categories = get_categories()
    dishes = get_dishes()
    return render_template("index.html", categories=categories, dishes=dishes)


# Меню: блюда по категориям
@app.route("/menu")
def menu():
    category_id = request.args.get("category_id")
    if category_id:
        dishes = get_dishes(category_id=int(category_id))
    else:
        dishes = get_dishes()
    categories = get_categories()
    return render_template("menu.html", dishes=dishes, categories=categories)


# Выдача загруженных файлов (например, изображений)
@app.route("/uploads/<filename>")
def uploads(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


# Получить корзину из сессии
def get_cart():
    return session.get("cart", {})


# Страница заказов пользователя
@app.route('/orders')
@login_required
def orders():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']

    orders_data = query_db("SELECT * FROM orders WHERE user_id = ? ORDER BY created_at DESC", (user_id,))

    orders = []
    for order_row in orders_data:
        order_id = order_row['id']
        items_data = query_db("""
            SELECT dishes.title, dishes.price, order_items.qty
            FROM order_items 
            JOIN dishes ON order_items.dish_id = dishes.id
            WHERE order_items.order_id = ?
        """, (order_id,))

        items = []
        total = 0
        for item in items_data:
            items.append({
                'dish_title': item['title'],
                'price': item['price'],
                'qty': item['qty']
            })
            total += item['price'] * item['qty']

        orders.append({
            'id': order_id,
            'address': order_row['address'],
            'phone': order_row['phone'],
            'status': order_row['status'],
            'payment_method': order_row['payment_method'],
            'delivery_time': order_row['delivery_time'],
            'created_at': order_row['created_at'],
            'items': items,
            'total': total,
        })

    return render_template('orders.html', orders=orders)


# ---------------------- КОРЗИНА ----------------------

# Добавить блюдо в корзину, показать содержимое корзины
@app.route("/cart", methods=["GET", "POST"])
@login_required
def cart():
    if request.method == "POST":
        # Добавление в корзину
        dish_id = request.form.get("dish_id")
        qty = int(request.form.get("qty", 1))
        cart = session.get("cart", {})
        cart[dish_id] = cart.get(dish_id, 0) + qty
        session["cart"] = cart
        session.modified = True
        return '', 204

    # Получаем корзину из сессии
    cart = get_cart()

    # Получаем блюда из базы
    full_items = []
    total_price = 0

    for dish_id_str, qty in cart.items():
        dish = get_dish_by_id(int(dish_id_str))
        if dish:
            subtotal = dish["price"] * qty
            total_price += subtotal
            full_items.append({
                "id": dish["id"],
                "title": dish["title"],
                "price": dish["price"],
                "image": dish["image"],
                "quantity": qty,
                "subtotal": subtotal
            })

    return render_template("cart.html", cart_items=full_items, total=total_price)


# Удалить блюдо из корзины
@app.route("/cart/remove/<int:dish_id>", methods=["POST"])
@login_required
def cart_remove(dish_id):
    cart = session.get("cart", {})
    cart.pop(str(dish_id), None)
    session["cart"] = cart
    session.modified = True
    return redirect(url_for("cart"))


# Изменить количество блюда в корзине
@app.route("/cart/update/<int:dish_id>", methods=["POST"])
@login_required
def cart_update_quantity(dish_id):
    qty = request.form.get("quantity", type=int)
    if not qty or qty < 1:
        qty = 1
    cart = session.get("cart", {})
    cart[str(dish_id)] = qty
    session["cart"] = cart
    session.modified = True
    return '', 204  # пустой успешный ответ


# ---------------------- ОФОРМЛЕНИЕ ЗАКАЗА ----------------------

# Статус заказа — страница с деталями заказа для пользователя
@app.route("/order_status/<int:order_id>")
def order_status(order_id):
    conn = get_db()
    cur = conn.cursor()

    order = cur.execute(
        "SELECT * FROM orders WHERE id = ? AND user_id = ?",
        (order_id, session["user_id"])
    ).fetchone()

    if order is None:
        flash("Заказ не найден или у вас нет доступа к нему.")
        return redirect(url_for("index"))

    items = cur.execute(
        """
        SELECT oi.qty AS quantity, d.title AS name, d.price
        FROM order_items oi
        JOIN dishes d ON oi.dish_id = d.id
        WHERE oi.order_id = ?
        """,
        (order_id,)
    ).fetchall()

    return render_template("order_status.html", order=order, items=items)


# Добавление отзыва к блюду
@app.route("/review/<int:dish_id>", methods=["POST"])
@login_required
def add_review_route(dish_id):
    rating = int(request.form.get("rating", 5))
    text = request.form.get("text", "")
    add_review(session["user_id"], dish_id, rating, text)
    flash("Спасибо за отзыв!")
    return redirect(url_for("dish_detail", dish_id=dish_id))


# Детальная страница блюда с отзывами
@app.route("/dish/<int:dish_id>")
def dish_detail(dish_id):
    dish = get_dish_by_id(dish_id)
    reviews = get_reviews_for_dish(dish_id)
    return render_template("dish_detail.html", dish=dish, reviews=reviews)


# Оформление заказа через /checkout 
@app.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():
    cart = get_cart()
    if not cart:
        flash("Корзина пуста!")
        return redirect(url_for("cart"))

    if request.method == "POST":
        name = request.form.get("name")
        phone = request.form.get("phone")
        address = request.form.get("address")
        delivery_time = request.form.get("delivery_time")
        payment_method = request.form.get("payment_method")

        items = {int(k): v for k, v in cart.items()}

        order_id = place_order(
            session["user_id"],
            items,
            address,
            phone,
            delivery_time,
            payment_method
        )

        session["cart"] = {}
        flash(f"Заказ оформлен! Номер заказа {order_id}")
        return redirect(url_for("order_status", order_id=order_id))

    return render_template("checkout.html")


# ---------------------- АДМИНКА ----------------------

# Админ-панель: просмотр заказов и добавление блюда
@app.route('/admin/dashboard', methods=['GET', 'POST'])
@admin_required
def dashboard():
    conn = get_db()
    cur = conn.cursor()

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        price = request.form.get('price')
        category_id = request.form.get('category')
        image = ''  # Пока без загрузки файла, можно добавить потом

        if not (title and description and price and category_id):
            flash("Заполните все поля!", "error")
        else:
            cur.execute("""
                INSERT INTO dishes (title, description, price, category_id, image)
                VALUES (?, ?, ?, ?, ?)
            """, (title, description, float(price), int(category_id), image))
            conn.commit()
            flash("Блюдо добавлено!", "success")
            return redirect(url_for('dashboard'))

    cur.execute("SELECT id, name FROM categories")
    categories = cur.fetchall()

    cur.execute("""
        SELECT o.id, u.name, o.address, o.phone, o.status,
               GROUP_CONCAT(d.title || ' (x' || oi.qty || ')', ', ') AS items
        FROM orders o
        JOIN users u ON o.user_id = u.id
        JOIN order_items oi ON oi.order_id = o.id
        JOIN dishes d ON oi.dish_id = d.id
        WHERE o.status != 'Доставлен'
        GROUP BY o.id
        ORDER BY o.created_at DESC
    """)
    orders = cur.fetchall()

    conn.close()

    return render_template('admin/dashboard.html', categories=categories, orders=orders)
