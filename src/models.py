class User:
    def __init__(self, id, email, name, is_admin=False, blocked=False):
        self.id = id
        self.email = email
        self.name = name
        self.is_admin = is_admin  # Флаг: админ или нет
        self.blocked = blocked    # Флаг: заблокирован или нет


class Category:
    def __init__(self, id, name):
        self.id = id
        self.name = name


class Dish:
    def __init__(self, id, title, description, price, category_id, image, is_veg=False, is_spicy=False):
        self.id = id
        self.title = title               # Название блюда
        self.description = description   # Описание блюда
        self.price = price               # Цена блюда
        self.category_id = category_id   # ID категории (связь с Category)
        self.image = image               # Имя файла или URL картинки
        self.is_veg = is_veg             # Вегетарианское ли блюдо
        self.is_spicy = is_spicy         # Острое ли блюдо


class Order:
    def __init__(self, id, user_id, address, phone, status, delivery_time, payment_method, created_at):
        self.id = id
        self.user_id = user_id               # ID пользователя (связь с User)
        self.address = address               # Адрес доставки
        self.phone = phone                   # Телефон
        self.status = status                 # Статус заказа (новый, в доставке, завершён и т.д.)
        self.delivery_time = delivery_time   # Время доставки
        self.payment_method = payment_method # Способ оплаты
        self.created_at = created_at         # Дата и время создания заказа


class Review:
    def __init__(self, id, user_id, dish_id, rating, text, created_at):
        self.id = id
        self.user_id = user_id           # ID пользователя
        self.dish_id = dish_id           # ID блюда
        self.rating = rating             # Оценка
        self.text = text                 # Текст отзыва
        self.created_at = created_at     # Дата создания отзыва