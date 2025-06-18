import sqlite3
import os
from flask import g

# Определяем путь к корневой папке проекта и к файлу базы данных
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "pasta_pizza.db")


# Получаем соединение с базой данных SQLite
# Если соединение уже есть в контексте Flask (g), возвращаем его
# Иначе создаём новое соединение и сохраняем в g

def get_db():
    if 'db' not in g:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # Результаты возвращаются в виде словарей
        g.db = conn
    return g.db


# Закрываем соединение с базой данных, если оно существует

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


# Инициализация базы данных: читаем SQL-скрипт и выполняем его

def init_db():
    db = get_db()
    with open("schema.sql", "r", encoding="utf-8") as f:
        db.executescript(f.read())


# Выполнить SELECT-запрос
# Возвращает все найденные записи или одну запись, если one=True

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


# Выполнить INSERT/UPDATE/DELETE-запрос и зафиксировать изменения
# Возвращает ID последней вставленной записи

def execute_db(query, args=()):
    db = get_db()
    cur = db.execute(query, args)
    db.commit()
    return cur.lastrowid
