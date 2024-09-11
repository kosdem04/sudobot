from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
import app.database.requests as db



# функция для отображения Inline кнопок выбора языка
async def select_role():
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text="😁 Заказчик",
                                callback_data="client"))
    kb.add(InlineKeyboardButton(text="🧑‍💻 Разработчик",
                                callback_data="developer"))
    kb.adjust(2)  # количество кнопок в одной строке
    # возвращаем клавиатуру с параметром для отображения клавиатуры на разных устройствах
    return kb.as_markup()


"""

Клавиатура для заказчиков
----------------------------------------------------------------------------------------------
"""

# главное меню клиента
client_main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='🔹 Мои заказы'),
     KeyboardButton(text='💥 Отклики')],
    [KeyboardButton(text='⏳ История заказов'),
     KeyboardButton(text='⭐️ Отзывы')],
    [KeyboardButton(text='💎 FAQ'),
     KeyboardButton(text='🧑‍💻 Стать разработчиком')],
], resize_keyboard=True)  # параметр для отображения клавиатуры на разных устройствах


# клавиатура для кнопки Назад
back = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='◀️ Назад')],],
                           resize_keyboard=True)  # параметр для отображения клавиатуры на разных устройствах


# клавиатура для кнопки Отмена
cancel = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='❌ Отмена')],],
                             resize_keyboard=True)  # параметр для отображения клавиатуры на разных устройствах


# клавиатура для кнопок Назад и Отмена
back_and_cancel = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='◀️ Назад')],
                                                [KeyboardButton(text='❌ Отмена')]],
                                      resize_keyboard=True)  # параметр для отображения клавиатуры на разных устройствах


sure = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='🌟 Да'),
                                      KeyboardButton(text='❌ Отмена')]],
                                      resize_keyboard=True)  # параметр для отображения клавиатуры на разных устройствах


create_and_back = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='➕ Создать заказ')],
                                                [KeyboardButton(text='◀️ Назад')]],
                                      resize_keyboard=True)  # параметр для отображения клавиатуры на разных устройствах


# функция для отображения Inline кнопок всех заказов пользователя
async def client_orders(orders):
    kb = InlineKeyboardBuilder()
    for order in orders:
        # каждый заказ оборачиваем в Inline кнопку
        kb.add(InlineKeyboardButton(text=f"{order.title}",
                                    callback_data=f"order_{order.id}"))
    kb.adjust(1)  # количество кнопок в одной строке
    # возвращаем клавиатуру с параметром для отображения клавиатуры на разных устройствах
    return kb.as_markup()


# меню клиента, когда он открывает подробности своего заказа
client_order_menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='✍️ Изменить заказ'),
     KeyboardButton(text='❌ Удалить заказ')],
    [KeyboardButton(text='🔹 В главное меню'),
     KeyboardButton(text='◀️ Назад')],
], resize_keyboard=True)  # параметр для отображения клавиатуры на разных устройствах


"""

Клавиатуры для разработчиков
----------------------------------------------------------------------------------------------
"""
# главное меню разработчика
developer_main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='💰 Биржа'),
     KeyboardButton(text='🧑‍💻 Мой профиль')],
    [KeyboardButton(text='🔹 Мои заказы'),
     KeyboardButton(text='⭐️ Отзывы')],
    [KeyboardButton(text='💎 FAQ'),
     KeyboardButton(text='😁 Стать заказчиком')],
], resize_keyboard=True)  # параметр для отображения клавиатуры на разных устройствах


# меню разработчика при переходе в "Мой профиль"
developer_profile = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='🤖 Выбрать тариф')],
    [KeyboardButton(text='◀️ Назад')]
], resize_keyboard=True)  # параметр для отображения клавиатуры на разных устройствах


# функция для отображения Inline кнопок всех заказов пользователя
async def select_tariff(tariff):
    kb = InlineKeyboardBuilder()
    # каждый заказ оборачиваем в Inline кнопку
    kb.add(InlineKeyboardButton(text=f"Выбрать тариф",
                                    callback_data=f"tariff_{tariff.id}"))
    kb.adjust(1)  # количество кнопок в одной строке
    # возвращаем клавиатуру с параметром для отображения клавиатуры на разных устройствах
    return kb.as_markup()


"""

Клавиатуры для администраторов
----------------------------------------------------------------------------------------------
"""
# функция для отображения Inline кнопок для модерации заказов
async def order_moderation(order_id):
    kb = InlineKeyboardBuilder()
    # каждый запрос оборачиваем в Inline кнопку
    kb.add(InlineKeyboardButton(text="✅ Разрешить",
                                callback_data=f"moderation-passed_{order_id}"))
    kb.add(InlineKeyboardButton(text="⛔ Запретить",
                                callback_data=f"moderation-failed_{order_id}"))
    kb.adjust(2)  # количество кнопок в одной строке
    # возвращаем клавиатуру с параметром для отображения клавиатуры на разных устройствах
    return kb.as_markup()


# функция для отображения Inline кнопок для модерации разработчиков
async def developer_moderation(developer_id):
    kb = InlineKeyboardBuilder()
    # каждый запрос оборачиваем в Inline кнопку
    kb.add(InlineKeyboardButton(text="✅ Разрешить",
                                callback_data=f"moderation-passed_{developer_id}"))
    kb.add(InlineKeyboardButton(text="⛔ Запретить",
                                callback_data=f"moderation-failed_{developer_id}"))
    kb.adjust(2)  # количество кнопок в одной строке
    # возвращаем клавиатуру с параметром для отображения клавиатуры на разных устройствах
    return kb.as_markup()