import sqlite3

# Запрашиваем у пользователя email
email = input("Введите ваш email, чтобы получить админ-права: ")

# Подключаемся к базе данных
conn = sqlite3.connect("pasta_pizza.db")
c = conn.cursor()

# Выполняем SQL-запрос: обновляем флаг is_admin для пользователя с указанным email
c.execute("UPDATE users SET is_admin=1 WHERE email=?", (email,))

# Сохраняем изменения и закрываем подключение
conn.commit()
conn.close()

print("Готово! Теперь вы админ.")