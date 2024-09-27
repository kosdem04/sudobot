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
     KeyboardButton(text='😁 Мой профиль')],
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


create_and_back = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='➕ Создать')],
                                                [KeyboardButton(text='◀️ Назад')]],
                                      resize_keyboard=True)  # параметр для отображения клавиатуры на разных устройствах


# функция для отображения Inline кнопок всех заказов пользователя
async def client_orders(orders, page, total_pages):
    kb = InlineKeyboardBuilder()
    for order in orders:
        # каждый заказ оборачиваем в Inline кнопку
        kb.add(InlineKeyboardButton(text=f"{order.title}",
                                    callback_data=f"order_{order.id}"))
    next_page = page + 1
    is_next = 0 if next_page > total_pages else 1
    if page > 1:
        kb.add(InlineKeyboardButton(text="⬅️", callback_data=f"prev-client-order_{page - 1}"))
    if is_next == 1:
        kb.add(InlineKeyboardButton(text="➡️", callback_data=f"next-client-order_{page + 1}"))
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


# функция для отображения Inline кнопки всех откликов для заказа
async def order_total_response(order_id, total_response):
    kb = InlineKeyboardBuilder()
    if total_response == 0:
        kb.add(InlineKeyboardButton(text="Нет откликов",
                                    callback_data="no_responses"))
    else:
        kb.add(InlineKeyboardButton(text=f"Посмотреть отклики ({total_response})",
                                    callback_data=f"total-order-responses_{order_id}"))
    kb.adjust(1)  # количество кнопок в одной строке
    # возвращаем клавиатуру с параметром для отображения клавиатуры на разных устройствах
    return kb.as_markup()


# функция для отображения Inline кнопок всех заказов пользователя
async def order_total_response_pagination(orders, page, total_pages):
    kb = InlineKeyboardBuilder()
    for order in orders:
        total_response = await db.total_response(order.id)
        # каждый заказ оборачиваем в Inline кнопку
        title = order.title if len(order.title) < 25 else f'{order.title[:25]}...'
        kb.add(InlineKeyboardButton(text=f"{title} (Отклики: {total_response})",
                                    callback_data=f"{f'total-order-responses_{order.id}' if total_response > 0
                                    else 'no_responses'}"))
    next_page = page + 1
    is_next = 0 if next_page > total_pages else 1
    if page > 1:
        kb.add(InlineKeyboardButton(text="⬅️", callback_data=f"prev-responses-for-order_{page - 1}"))
    if is_next == 1:
        kb.add(InlineKeyboardButton(text="➡️", callback_data=f"next-responses-for-order_{page + 1}"))
    kb.adjust(1)  # количество кнопок в одной строке
    # возвращаем клавиатуру с параметром для отображения клавиатуры на разных устройствах
    return kb.as_markup()


# функция для отображения Inline кнопок всех заказов пользователя
async def client_responses_for_order_pagination(responses, page, total_pages):
    kb = InlineKeyboardBuilder()
    for response in responses:
        # каждый заказ оборачиваем в Inline кнопку
        title = response.description if len(response.description) < 35 else f'{response.description[:25]}...'
        kb.add(InlineKeyboardButton(text=f"{title}",
                                    callback_data=f'client-response-info_{response.id}'))
    next_page = page + 1
    is_next = 0 if next_page > total_pages else 1
    if page > 1:
        kb.add(InlineKeyboardButton(text="⬅️", callback_data=f"prev-client-response-info_{page - 1}"))
    if is_next == 1:
        kb.add(InlineKeyboardButton(text="➡️", callback_data=f"next-client-response-info_{page + 1}"))
    kb.add(InlineKeyboardButton(text="🔙 Вернуться к списку заказов", callback_data="back_to_total_order_responses"))
    kb.adjust(1)  # количество кнопок в одной строке
    # возвращаем клавиатуру с параметром для отображения клавиатуры на разных устройствах
    return kb.as_markup()


# функция для отображения Inline кнопок всех заказов пользователя
async def back_to_total_order_responses():
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text="🔙 Вернуться к списку заказов", callback_data="back_to_total_order_responses"))
    kb.adjust(1)  # количество кнопок в одной строке
    # возвращаем клавиатуру с параметром для отображения клавиатуры на разных устройствах
    return kb.as_markup()


# функция для отображения Inline кнопок для показа меню клиенту в отклике
async def client_response_menu(developer_username, response):
    # Создаем инстанс клавиатуры
    kb = InlineKeyboardBuilder()

    # Создаем кнопки
    button1 = InlineKeyboardButton(text="Написать разработчику", url=f"https://t.me/{developer_username}")
    button2 = InlineKeyboardButton(text="Заказ выполнен", callback_data=f"choose-response_{response.id}")
    button3 = InlineKeyboardButton(text="Отказать", callback_data=f"refusal-response_{response.id}")
    button4 = InlineKeyboardButton(text="Скрыть", callback_data="hide_client_response_info")

    # Добавляем первую кнопку на первую строку
    kb.add(button1)
    if response.developer_rel.rating > 0:
        kb.row(InlineKeyboardButton(text="Последние отзывы о разработчике",
                                    callback_data=f"the-last-feedbacks-about-developer_{response.developer_rel.tg_id}"))
    # Добавляем две другие кнопки на одну строку
    kb.row(button2, button3)

    kb.row(button4)
    # возвращаем клавиатуру с параметром для отображения клавиатуры на разных устройствах
    return kb.as_markup()


# функция для отображения Inline кнопок для подтверждения выполнения заказа
async def sure_complete_order(response_id):
    # Создаем инстанс клавиатуры
    kb = InlineKeyboardBuilder()

    # Создаем кнопки
    button2 = InlineKeyboardButton(text="🌟 Да", callback_data=f"order-complete_{response_id}")
    button3 = InlineKeyboardButton(text="❌ Отмена", callback_data=f"cancel-order-complete_{response_id}")

    # Добавляем две другие кнопки на одну строку
    kb.row(button2, button3)
    # возвращаем клавиатуру с параметром для отображения клавиатуры на разных устройствах
    return kb.as_markup()


# функция для отображения Inline кнопок всех заказов пользователя
async def client_history_orders(orders, page, total_pages):
    kb = InlineKeyboardBuilder()
    for order in orders:
        # каждый заказ оборачиваем в Inline кнопку
        kb.add(InlineKeyboardButton(text=f"{order.title}",
                                    callback_data=f"history-order_{order.id}"))
    next_page = page + 1
    is_next = 0 if next_page > total_pages else 1
    if page > 1:
        kb.add(InlineKeyboardButton(text="⬅️", callback_data=f"prev-client-history-order_{page - 1}"))
    if is_next == 1:
        kb.add(InlineKeyboardButton(text="➡️", callback_data=f"next-client-history-order_{page + 1}"))
    kb.adjust(1)  # количество кнопок в одной строке
    # возвращаем клавиатуру с параметром для отображения клавиатуры на разных устройствах
    return kb.as_markup()


# функция для отображения Inline кнопки 'Подробнее' для просмотра деталей заказа
async def history_order_info(order):
    kb = InlineKeyboardBuilder()
    # каждый заказ оборачиваем в Inline кнопку
    if not await db.is_feedback_about_developer(order.id):
        kb.add(InlineKeyboardButton(text="Оценить",
                                    callback_data=f"client-create-feedback_{order.id}"))
    else:
        kb.add(InlineKeyboardButton(text="Изменить отзыв",
                                    callback_data=f"client-edit-feedback_{order.id}"))
    kb.add(InlineKeyboardButton(text="Скрыть",
                                callback_data="hide_history_order_info"))
    kb.adjust(1)  # количество кнопок в одной строке
    # возвращаем клавиатуру с параметром для отображения клавиатуры на разных устройствах
    return kb.as_markup()


# функция для отображения Inline кнопки 'Подробнее' для просмотра деталей заказа
async def client_feedback_info():
    kb = InlineKeyboardBuilder()
    # каждый заказ оборачиваем в Inline кнопку
    kb.add(InlineKeyboardButton(text="Скрыть",
                                callback_data="hide_client_feedback_info"))
    kb.adjust(1)  # количество кнопок в одной строке
    # возвращаем клавиатуру с параметром для отображения клавиатуры на разных устройствах
    return kb.as_markup()


# функция для отображения Inline кнопки 'Подробнее' для просмотра деталей заказа
async def backs(object_id):
    kb = InlineKeyboardBuilder()
    # каждый заказ оборачиваем в Inline кнопку
    kb.add(InlineKeyboardButton(text="◀️ Назад",
                                callback_data=f"back_{object_id}"))
    kb.adjust(1)  # количество кнопок в одной строке
    # возвращаем клавиатуру с параметром для отображения клавиатуры на разных устройствах
    return kb.as_markup()


"""

Клавиатуры для разработчиков
----------------------------------------------------------------------------------------------
"""
# главное меню разработчика
developer_main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='💰 Биржа'),
     KeyboardButton(text='💥️ Мои отклики')],
    [KeyboardButton(text='🔹 Выполненные заказы'),
     KeyboardButton(text='🧑‍💻 Мой профиль')],
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


# функция для отображения Inline кнопки 'Подробнее' для просмотра деталей заказа
'''async def order_info(order_id):
    kb = InlineKeyboardBuilder()
    # каждый заказ оборачиваем в Inline кнопку
    kb.add(InlineKeyboardButton(text=f"Подробнее",
                                callback_data=f"order-info_{order_id}"))
    kb.adjust(1)  # количество кнопок в одной строке
    # возвращаем клавиатуру с параметром для отображения клавиатуры на разных устройствах
    return kb.as_markup()'''


async def all_orders_pagination(orders, page, total_pages):
    kb = InlineKeyboardBuilder()

    for order in orders:
        kb.add(InlineKeyboardButton(text=f"{order.title}",
                                    callback_data=f"order-info_{order.id}"))
    next_page = page + 1
    is_next = 0  if next_page > total_pages else 1
    if page > 1:
        kb.add(InlineKeyboardButton(text="⬅️", callback_data=f"prev-market-order_{page-1}"))
    if is_next == 1:
        kb.add(InlineKeyboardButton(text="➡️", callback_data=f"next-market-order_{page+1}"))
    kb.adjust(1)
    return kb.as_markup()


async def back_from_order_info():
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text="◀️ Назад",
                                callback_data="back_from_order_info"))
    kb.adjust(1)
    return kb.as_markup()


# функция для отображения Inline кнопки 'Подробнее' для просмотра деталей заказа
async def market_order_info():
    kb = InlineKeyboardBuilder()
    # каждый заказ оборачиваем в Inline кнопку
    kb.add(InlineKeyboardButton(text="Скрыть",
                                callback_data="hide_market_order_info"))
    kb.adjust(1)  # количество кнопок в одной строке
    # возвращаем клавиатуру с параметром для отображения клавиатуры на разных устройствах
    return kb.as_markup()


# функция для отображения Inline кнопки 'Откликнуться' для отклика на заказ
async def make_response(order):
    kb = InlineKeyboardBuilder()
    # каждый заказ оборачиваем в Inline кнопку
    if order.client_rel.rating > 0:
        kb.add(InlineKeyboardButton(text="Последние отзывы о заказчике",
                                    callback_data=f"the-last-feedbacks-about-client_{order.client_rel.tg_id}"))
    kb.add(InlineKeyboardButton(text="Откликнуться",
                                callback_data=f"make-response_{order.id}"))
    kb.add(InlineKeyboardButton(text="Скрыть",
                                callback_data="hide_market_order_info"))
    kb.adjust(1)  # количество кнопок в одной строке
    # возвращаем клавиатуру с параметром для отображения клавиатуры на разных устройствах
    return kb.as_markup()


# функция для отображения Inline кнопки 'Подробнее' для просмотра деталей заказа
async def delete_response(response_id):
    kb = InlineKeyboardBuilder()
    # каждый заказ оборачиваем в Inline кнопку
    kb.add(InlineKeyboardButton(text="Удалить отклик",
                                callback_data=f"delete-response_{response_id}"))
    kb.add(InlineKeyboardButton(text="Скрыть",
                                callback_data="hide_developer_response_info"))
    kb.adjust(1)  # количество кнопок в одной строке
    # возвращаем клавиатуру с параметром для отображения клавиатуры на разных устройствах
    return kb.as_markup()


# функция для отображения Inline кнопок для подтверждения выполнения заказа
async def sure_delete_response(response_id):
    # Создаем инстанс клавиатуры
    kb = InlineKeyboardBuilder()

    # Создаем кнопки
    button2 = InlineKeyboardButton(text="🌟 Да", callback_data=f"ok-delete-response_{response_id}")
    button3 = InlineKeyboardButton(text="❌ Отмена", callback_data=f"cancel-delete-response_{response_id}")

    # Добавляем две другие кнопки на одну строку
    kb.row(button2, button3)
    # возвращаем клавиатуру с параметром для отображения клавиатуры на разных устройствах
    return kb.as_markup()


async def completed_orders_pagination(orders, page, total_pages):
    kb = InlineKeyboardBuilder()

    for order in orders:
        kb.add(InlineKeyboardButton(text=f"{order.title}",
                                    callback_data=f"completed-order-info_{order.id}"))
    next_page = page + 1
    is_next = 0  if next_page > total_pages else 1
    if page > 1:
        kb.add(InlineKeyboardButton(text="⬅️", callback_data=f"prev-completed-order_{page-1}"))
    if is_next == 1:
        kb.add(InlineKeyboardButton(text="➡️", callback_data=f"next-completed-order_{page+1}"))
    kb.adjust(1)
    return kb.as_markup()


# функция для отображения Inline кнопки 'Подробнее' для просмотра деталей заказа
async def completed_orders_menu(order_id):
    kb = InlineKeyboardBuilder()
    # каждый заказ оборачиваем в Inline кнопку
    kb.add(InlineKeyboardButton(text="Подробнее",
                                callback_data=f"completed-order-info_{order_id}"))
    kb.adjust(1)  # количество кнопок в одной строке
    # возвращаем клавиатуру с параметром для отображения клавиатуры на разных устройствах
    return kb.as_markup()


# функция для отображения Inline кнопки 'Подробнее' для просмотра деталей заказа
async def completed_order_info(order):
    kb = InlineKeyboardBuilder()
    # каждый заказ оборачиваем в Inline кнопку
    if not await db.is_feedback_about_client(order.id):
        kb.add(InlineKeyboardButton(text="Оценить",
                                    callback_data=f"developer-create-feedback_{order.id}"))
    else:
        kb.add(InlineKeyboardButton(text="Изменить отзыв",
                                    callback_data=f"developer-edit-feedback_{order.id}"))
    kb.add(InlineKeyboardButton(text="Скрыть",
                                callback_data="hide_completed_order_info"))
    kb.adjust(1)  # количество кнопок в одной строке
    # возвращаем клавиатуру с параметром для отображения клавиатуры на разных устройствах
    return kb.as_markup()


# функция для отображения Inline кнопок всех заказов пользователя
async def developer_responses_pagination(responses, page, total_pages):
    kb = InlineKeyboardBuilder()
    for response in responses:
        # каждый заказ оборачиваем в Inline кнопку
        kb.add(InlineKeyboardButton(text=f"{response.description}",
                                    callback_data=f"developer-response-info_{response.id}"))
    next_page = page + 1
    is_next = 0 if next_page > total_pages else 1
    if page > 1:
        kb.add(InlineKeyboardButton(text="⬅️", callback_data=f"prev-developer-responses_{page - 1}"))
    if is_next == 1:
        kb.add(InlineKeyboardButton(text="➡️", callback_data=f"next-developer-responses_{page + 1}"))
    kb.adjust(1)  # количество кнопок в одной строке
    # возвращаем клавиатуру с параметром для отображения клавиатуры на разных устройствах
    return kb.as_markup()


# функция для отображения Inline кнопок для подтверждения выполнения заказа
async def free_payment(tariff_id):
    # Создаем инстанс клавиатуры
    kb = InlineKeyboardBuilder()

    # Создаем кнопки
    button = InlineKeyboardButton(text="Бесплатно", callback_data=f"free-payment_{tariff_id}")

    # Добавляем две другие кнопки на одну строку
    kb.row(button)
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


# главное меню клиента
admin_panel = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='🤖 Тарифы'),
     KeyboardButton(text='✍️ Сделать рассылку')],
    [KeyboardButton(text='◀️ Выйти')],
], resize_keyboard=True)  # параметр для отображения клавиатуры на разных устройствах


# функция для отображения Inline кнопок всех заказов пользователя
async def tariff_menu(tariff):
    kb = InlineKeyboardBuilder()
    # каждый заказ оборачиваем в Inline кнопку
    kb.add(InlineKeyboardButton(text=f"Изменить тариф",
                                callback_data=f"admin-edit-tariff_{tariff.id}"))
    kb.add(InlineKeyboardButton(text=f"Удалить тариф",
                                callback_data=f"admin-delete-tariff_{tariff.id}"))
    kb.adjust(1)  # количество кнопок в одной строке
    # возвращаем клавиатуру с параметром для отображения клавиатуры на разных устройствах
    return kb.as_markup()


tariffs_menu = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='➕ Добавить тариф')],
                                                [KeyboardButton(text='◀️ Назад')]],
                                      resize_keyboard=True)  # параметр для отображения клавиатуры на разных устройствах


# функция для отображения Inline кнопок для подтверждения выполнения заказа
async def sure_delete_tariff(tariff_id):
    # Создаем инстанс клавиатуры
    kb = InlineKeyboardBuilder()

    # Создаем кнопки
    button2 = InlineKeyboardButton(text="🌟 Да", callback_data=f"ok-delete-tariff_{tariff_id}")
    button3 = InlineKeyboardButton(text="❌ Отмена", callback_data=f"cancel-delete-tariff_{tariff_id}")

    # Добавляем две другие кнопки на одну строку
    kb.row(button2, button3)
    # возвращаем клавиатуру с параметром для отображения клавиатуры на разных устройствах
    return kb.as_markup()


# функция для отображения Inline кнопок для подтверждения выполнения заказа
async def sendall_methods():
    # Создаем инстанс клавиатуры
    kb = InlineKeyboardBuilder()

    # Создаем кнопки
    button1 = InlineKeyboardButton(text="💥 Отправить всем", callback_data="sendall_1")
    button2 = InlineKeyboardButton(text="😁 Отправить заказчикам", callback_data="sendall_2")
    button3 = InlineKeyboardButton(text="🧑‍💻 Отправить разработчикам", callback_data="sendall_3")

    kb.add(button1)
    # Добавляем две другие кнопки на одну строку
    kb.row(button2, button3)
    # возвращаем клавиатуру с параметром для отображения клавиатуры на разных устройствах
    return kb.as_markup()