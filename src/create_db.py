import sqlite3
import os

# Получаем абсолютный путь к директории на уровень выше текущего файла
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Формируем полный путь к файлу базы данных
conn = sqlite3.connect(os.path.join(BASE_DIR, "pasta_pizza.db"))  # <-- В твоем коде была ошибка: нужно .connect()

# Создаем объект курсора для выполнения SQL-запросов
cur = conn.cursor()

# Таблица пользователей
cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE,                -- Уникальный email пользователя
    name TEXT,                        -- Имя пользователя
    password TEXT,                    -- Хэш пароля
    is_admin INTEGER DEFAULT 0        -- Флаг администратора: 0 или 1
)
""")

# Таблица категорий блюд (например, пицца, паста, напитки)
cur.execute("""
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL                -- Название категории
)
""")

# Таблица блюд
cur.execute("""
CREATE TABLE IF NOT EXISTS dishes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,                       -- Название блюда
    description TEXT,                  -- Описание
    price REAL,                       -- Цена
    category_id INTEGER,              -- Ссылка на категорию
    image TEXT,                       -- Путь к изображению
    is_veg INTEGER DEFAULT 0,         -- Вегетарианское ли блюдо
    is_spicy INTEGER DEFAULT 0,       -- Острое ли блюдо
    FOREIGN KEY(category_id) REFERENCES categories(id)
)
""")

# Таблица заказов
cur.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,                  -- Ссылка на пользователя
    address TEXT,                     -- Адрес доставки
    phone TEXT,                       -- Телефон для связи
    status TEXT,                      -- Статус заказа
    created_at TEXT,                  -- Дата создания
    payment_method TEXT,              -- Способ оплаты
    delivery_time TEXT,               -- Ожидаемое время доставки
    FOREIGN KEY(user_id) REFERENCES users(id)
)
""")

# Таблица элементов заказа (какие блюда и сколько)
cur.execute("""
CREATE TABLE IF NOT EXISTS order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER,                 -- Ссылка на заказ
    dish_id INTEGER,                  -- Ссылка на блюдо
    qty INTEGER,                      -- Количество
    FOREIGN KEY(order_id) REFERENCES orders(id),
    FOREIGN KEY(dish_id) REFERENCES dishes(id)
)
""")

# Таблица отзывов пользователей на блюда
cur.execute("""
CREATE TABLE IF NOT EXISTS reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,                  -- Кто оставил отзыв
    dish_id INTEGER,                  -- На какое блюдо
    rating INTEGER,                   -- Оценка (звёзды)
    text TEXT,                        -- Текст отзыва
    created_at TEXT,                  -- Дата создания
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(dish_id) REFERENCES dishes(id)
)
""")

# Сохраняем все изменения в базе данных
conn.commit()

# Закрываем соединение с базой
conn.close()