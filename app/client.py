from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from sqlalchemy.util import await_only

import app.database.requests as db
import app.states as st
import app.keyboards as kb

from config import ADMIN_ORDER_CHAT_ID

client = Router()


@client.message(F.text == 'Чат')
async def cmd_start(message: Message, state: FSMContext):
    await message.answer(f'ID: {message.chat.id}')


@client.message(F.text == '◀️ Назад', st.Register.role)
@client.message(F.text == '◀️ Назад', st.Register.moderation)
@client.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        if await db.is_client(message.from_user.id):
            await state.clear()
            # устанавливаем нужное FSM состояние
            await state.set_state(st.ClientMenu.menu)
            await message.answer('Главное меню', reply_markup=kb.client_main)
        elif await db.is_developer(message.from_user.id):
                await state.clear()
                # устанавливаем нужное FSM состояние
                await state.set_state(st.DeveloperMenu.menu)
                await message.answer('Главное меню', reply_markup=kb.developer_main)
        else:
            await state.set_state(st.Register.role)
            await message.answer('Добро пожаловать в бот!\n'
                                 'Выберете вашу роль 👇', reply_markup=await kb.select_role())
    except Exception:
        await message.answer('Произошла ошибка\n'
                             'Введите команду /start или свяжитесь с @mesudoteach')


@client.callback_query(F.data == 'client', st.Register.role)
async def client_after_register_menu(callback: CallbackQuery, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        await state.clear()
        # устанавливаем нужное FSM состояние
        await state.set_state(st.ClientMenu.menu)
        await callback.answer('')
        # добавляем клиента в БД
        await db.add_client(callback.from_user.id)
        await callback.message.answer('Главное меню', reply_markup=kb.client_main)
    except Exception:
        await callback.message.answer('Произошла ошибка\n'
                             'Введите команду /start или свяжитесь с @mesudoteach')



@client.message(F.text == '◀️ Назад', st.ClientProfile.profile)
@client.message(F.text == '◀️ Назад', st.OrderHistory.list)
@client.message(F.text == '◀️ Назад', st.ClientResponse.list)
@client.message(F.text == '🔹 В главное меню', st.ClientOrder.order)
@client.message(F.text == '◀️ Назад', st.ClientOrder.list)
@client.message(F.text == '◀️ Назад', st.FAQ.client)
async def client_main_menu(message: Message, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        await state.clear()
        # устанавливаем нужное FSM состояние
        await state.set_state(st.ClientMenu.menu)
        await message.answer('Главное меню', reply_markup=kb.client_main)
    except Exception:
        await message.answer('Произошла ошибка\n'
                             'Введите команду /start или свяжитесь с @mesudoteach')


@client.message(F.text == '😁 Стать заказчиком', st.DeveloperMenu.menu)
async def become_client(message: Message, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        if await db.is_client(message.from_user.id):
            await state.clear()
            # устанавливаем нужное FSM состояние
            await state.set_state(st.ClientMenu.menu)
            await message.answer('Главное меню', reply_markup=kb.client_main)
        else:
            # добавляем клиента в БД
            await db.add_client(message.from_user.id)
            await state.clear()
            # устанавливаем нужное FSM состояние
            await state.set_state(st.ClientMenu.menu)
            await message.answer('Главное меню', reply_markup=kb.client_main)
    except Exception:
        await message.answer('Произошла ошибка\n'
                             'Введите команду /start или свяжитесь с @mesudoteach')




"""

Действия в разделе "Мои заказы"
----------------------------------------------------------------------------------------------
"""
@client.message(F.text == '❌ Отмена', st.AddOrder.sure)
@client.message(F.text == '❌ Отмена', st.AddOrder.description)
@client.message(F.text == '❌ Отмена', st.AddOrder.title)
@client.message(F.text == '◀️ Назад', st.ClientOrder.order)
@client.message(F.text == '🔹 Мои заказы', st.ClientMenu.menu)
async def client_order_list(message: Message, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        orders = await db.client_orders(message.from_user.id)
        if not orders:
            # устанавливаем нужное FSM состояние
            await state.set_state(st.ClientOrder.list)
            await message.answer('У вас нет ни одного заказа',
                                 reply_markup=kb.create_and_back)
        else:
            total_pages = (len(orders) + 5 - 1) // 5  # Общее количество страниц
            # устанавливаем нужное FSM состояние
            await state.set_state(st.ClientOrder.total_pages)
            await state.update_data(total_pages=total_pages)
            # устанавливаем нужное FSM состояние
            await state.set_state(st.ClientOrder.list)
            orders = await db.client_orders_pagination(message.from_user.id,1)
            await message.answer(f'<b>Страница 1 из {total_pages}</b>',
                                 reply_markup=await kb.client_orders(orders, 1, total_pages))
            await message.answer('Меню 👇',
                                 reply_markup=kb.create_and_back)
    except Exception:
        await message.answer('Произошла ошибка\n'
                             'Введите команду /start или свяжитесь с @mesudoteach')


@client.callback_query(F.data.startswith('prev-client-order_'), st.ClientOrder.list)
@client.callback_query(F.data.startswith('next-client-order_'), st.ClientOrder.list)
async def client_order_pagination(callback: CallbackQuery, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        await callback.answer('')
        page = int(callback.data.split('_')[1])
        orders = await db.client_orders_pagination(callback.from_user.id,page)
        tdata = await state.get_data()
        total_pages = tdata['total_pages']
        await callback.message.edit_text(f'<b>Страница {page} из {total_pages}</b>',
                             reply_markup=await kb.client_orders(orders, page, total_pages))
    except Exception:
        await callback.message.answer('Произошла ошибка\n'
                             'Введите команду /start или свяжитесь с @mesudoteach')


@client.callback_query(F.data.startswith('order_'), st.ClientOrder.list)
async def client_order_info(callback: CallbackQuery, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        # ответ на callback
        await callback.answer('Подробности заказа')
        # устанавливаем нужное FSM состояние
        await state.set_state(st.ClientOrder.order)
        # извлекаем из callback id запроса
        order_info = await db.get_order(callback.data.split('_')[1])
        # записываем в нужное нам состояние введённую информацию
        await state.update_data(order=callback.data.split('_')[1])
        await callback.message.answer(f'Подробности заказа 🔹 \n\n'
                                      f'<b>Название</b>: {order_info.title}\n'
                                      f'<b>Описание</b>:\n{order_info.description}\n\n'
                                      f'{f"<b>‼️ Заказ на модерации</b>" if not order_info.available else ""}',
                             reply_markup=kb.client_order_menu)
    except Exception:
        await callback.message.answer('Произошла ошибка\n'
                             'Введите команду /start или свяжитесь с @mesudoteach')


"""-------------------------------------------Создать заказ---------------------------------------------------"""
@client.message(F.text == '➕ Создать', st.ClientOrder.list)
async def order_title(message: Message, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        # устанавливаем нужное FSM состояние
        await state.set_state(st.AddOrder.title)
        await message.answer('Введите название заказа (до 50 символов)',
                             reply_markup=kb.cancel)
    except Exception:
        await message.answer('Произошла ошибка\n'
                             'Введите команду /start или свяжитесь с @mesudoteach')


@client.message(st.AddOrder.title)
async def order_description(message: Message, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        if len(message.text) > 50:
            await message.answer('Название заказа не должно быть более 50 символов',
                                 reply_markup=kb.cancel)
        else:
            # записываем в нужное нам состояние введённую информацию
            await state.update_data(title=message.text)
            # устанавливаем нужное FSM состояние
            await state.set_state(st.AddOrder.description)
            await message.answer('Введите описание заказа',
                                 reply_markup=kb.cancel)
    except Exception:
        await message.answer('Произошла ошибка\n'
                             'Введите команду /start или свяжитесь с @mesudoteach')


@client.message(st.AddOrder.description)
async def sure_add_order(message: Message, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        if len(message.text) > 10000:
            await message.answer('Описание заказа не должно быть более 1000 символов',
                                 reply_markup=kb.cancel)
        else:
            # записываем в нужное нам состояние введённую информацию
            await state.update_data(description=message.text)
            # берём данные из всех состояний
            tdata = await state.get_data()
            # устанавливаем нужное FSM состояние
            await state.set_state(st.AddOrder.sure)
            await message.answer(f'Вы уверены, что хотите создать заказ со следующими данными?\n\n'
                                 f'<b>Название</b>: {tdata['title']}\n'
                                 f'<b>Описание</b>:\n{tdata['description']}',
                                 reply_markup=kb.sure)
    except Exception:
        await message.answer('Произошла ошибка\n'
                             'Введите команду /start или свяжитесь с @mesudoteach')


@client.message(F.text == '🌟 Да', st.AddOrder.sure)
async def ok_add_order(message: Message, bot: Bot, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        # берём данные из всех состояний
        tdata = await state.get_data()
        # добавляем новый заказ в БД
        order = await db.add_order(message.from_user.id ,tdata['title'], tdata['description'])
        await bot.send_message(chat_id=ADMIN_ORDER_CHAT_ID, text=f'‼️ ВНИМАНИЕ ‼️\n\n'
                                                                 f'<b>Новый заказ:</b>\n'
                                                                 f'<b>TG_ID заказчика:</b> {message.from_user.id}\n'
                                                                 f'<b>Название:</b> {tdata['title']}\n'
                                                                 f'<b>Описание:</b>\n{tdata['description']}\n',
                               reply_markup=await kb.order_moderation(order.id))
        orders = await db.client_orders(message.from_user.id)
        await message.answer('‼️ Ваш заказ отправлен на модерацию')
        if not orders:
            # устанавливаем нужное FSM состояние
            await state.set_state(st.ClientOrder.list)
            await message.answer('У вас нет ни одного заказа',
                                 reply_markup=kb.create_and_back)
        else:
            total_pages = (len(orders) + 5 - 1) // 5  # Общее количество страниц
            # устанавливаем нужное FSM состояние
            await state.set_state(st.ClientOrder.total_pages)
            await state.update_data(total_pages=total_pages)
            # устанавливаем нужное FSM состояние
            await state.set_state(st.ClientOrder.list)
            orders = await db.client_orders_pagination(message.from_user.id, 1)
            await message.answer(f'<b>Страница 1 из {total_pages}</b>',
                                 reply_markup=await kb.client_orders(orders, 1, total_pages))
            await message.answer('Меню 👇',
                                 reply_markup=kb.create_and_back)
    except Exception:
        await message.answer('Произошла ошибка\n'
                             'Введите команду /start или свяжитесь с @mesudoteach')


"""--------------------------------Изменение заказа---------------------------------------------"""

@client.message(F.text == '✍️ Изменить заказ', st.ClientOrder.order)
async def client_order_edit_title(message: Message, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        # устанавливаем нужное FSM состояние
        await state.set_state(st.EditOrder.title)
        await message.answer('Введите новое название заказа (до 50 символов)',
                             reply_markup=kb.cancel)
    except Exception:
        await message.answer('Произошла ошибка\n'
                             'Введите команду /start или свяжитесь с @mesudoteach')


@client.message(F.text == '❌ Отмена', st.DeleteOrder.sure)
@client.message(F.text == '❌ Отмена', st.EditOrder.sure)
@client.message(F.text == '❌ Отмена', st.EditOrder.description)
@client.message(F.text == '❌ Отмена', st.EditOrder.title)
async def  cancel_client_order_edit(message: Message, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        # устанавливаем нужное FSM состояние
        await state.set_state(st.ClientOrder.order)
        tdata = await state.get_data()
        # извлекаем из callback id запроса
        order_info = await db.get_order(tdata['order'])
        await message.answer('Подробности заказа 🔹')
        await message.answer(f'<b>Название</b>: {order_info.title}\n'
                                      f'<b>Описание</b>:\n{order_info.description}',
                                      reply_markup=kb.client_order_menu)
    except Exception:
        await message.answer('Произошла ошибка\n'
                             'Введите команду /start или свяжитесь с @mesudoteach')


@client.message(st.EditOrder.title)
async def client_order_edit_description(message: Message, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        if len(message.text) > 50:
            await message.answer('Название заказа не должно быть более 50 символов',
                                 reply_markup=kb.cancel)
        else:
            # записываем в нужное нам состояние введённую информацию
            await state.update_data(title=message.text)
            # устанавливаем нужное FSM состояние
            await state.set_state(st.EditOrder.description)
            await message.answer('Введите новое описание заказа',
                                 reply_markup=kb.cancel)
    except Exception:
        await message.answer('Произошла ошибка\n'
                             'Введите команду /start или свяжитесь с @mesudoteach')


@client.message(st.EditOrder.description)
async def sure_client_order_edit(message: Message, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        if len(message.text) > 10000:
            await message.answer('Описание заказа не должно быть более 1000 символов',
                                 reply_markup=kb.cancel)
        else:
            # записываем в нужное нам состояние введённую информацию
            await state.update_data(description=message.text)
            # берём данные из всех состояний
            tdata = await state.get_data()
            # устанавливаем нужное FSM состояние
            await state.set_state(st.EditOrder.sure)
            await message.answer(f'Вы уверены, что хотите изменить данные заказа на следующие?\n\n'
                                 f'<b>Новое название</b>: {tdata['title']}\n'
                                 f'<b>Новое описание</b>:\n{tdata['description']}',
                                 reply_markup=kb.sure)
    except Exception:
        await message.answer('Произошла ошибка\n'
                             'Введите команду /start или свяжитесь с @mesudoteach')


@client.message(F.text == '🌟 Да', st.EditOrder.sure)
async def ok_edit_order(message: Message, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        # берём данные из всех состояний
        tdata = await state.get_data()
        # добавляем новый заказ в БД
        await db.edit_order(tdata['order'] ,tdata['title'], tdata['description'])
        # устанавливаем нужное FSM состояние
        await state.set_state(st.ClientOrder.order)
        tdata = await state.get_data()
        # извлекаем из callback id запроса
        order_info = await db.get_order(tdata['order'])
        await message.answer('Подробности заказа 🔹')
        await message.answer(f'<b>Название</b>: {order_info.title}\n'
                             f'<b>Описание</b>:\n{order_info.description}',
                             reply_markup=kb.client_order_menu)
    except Exception:
        await message.answer('Произошла ошибка\n'
                             'Введите команду /start или свяжитесь с @mesudoteach')


"""--------------------------------Удаление заказа---------------------------------------------"""
@client.message(F.text == '❌ Удалить заказ', st.ClientOrder.order)
async def client_order_delete(message: Message, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        # устанавливаем нужное FSM состояние
        await state.set_state(st.DeleteOrder.sure)
        await message.answer('Вы уверены, что хотите удалить данный заказ?',
                             reply_markup=kb.sure)
    except Exception:
        await message.answer('Произошла ошибка\n'
                             'Введите команду /start или свяжитесь с @mesudoteach')


@client.message(F.text == '🌟 Да', st.DeleteOrder.sure)
async def ok_delete_order(message: Message, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        # берём данные из всех состояний
        tdata = await state.get_data()
        # добавляем новый заказ в БД
        await db.delete_order(tdata['order'])
        orders = await db.client_orders(message.from_user.id)
        if not orders:
            # устанавливаем нужное FSM состояние
            await state.set_state(st.ClientOrder.list)
            await message.answer('У вас нет ни одного заказа',
                                 reply_markup=kb.create_and_back)
        else:
            total_pages = (len(orders) + 5 - 1) // 5  # Общее количество страниц
            # устанавливаем нужное FSM состояние
            await state.set_state(st.ClientOrder.total_pages)
            await state.update_data(total_pages=total_pages)
            # устанавливаем нужное FSM состояние
            await state.set_state(st.ClientOrder.list)
            orders = await db.client_orders_pagination(message.from_user.id, 1)
            await message.answer(f'<b>Страница 1 из {total_pages}</b>',
                                 reply_markup=await kb.client_orders(orders, 1, total_pages))
            await message.answer('Меню 👇',
                                 reply_markup=kb.create_and_back)
    except Exception:
        await message.answer('Произошла ошибка\n'
                             'Введите команду /start или свяжитесь с @mesudoteach')


"""

Действия в разделе "Отклики"
----------------------------------------------------------------------------------------------
"""
@client.message(F.text == '💥 Отклики', st.ClientMenu.menu)
async def client_response_list(message: Message, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        orders = await db.client_available_orders(message.from_user.id)
        if not orders:
            # устанавливаем нужное FSM состояние
            await state.set_state(st.ClientResponse.list)
            await message.answer('Нужен хотя бы один активный заказ',
                                 reply_markup=kb.create_and_back)
        else:
            # устанавливаем нужное FSM состояние
            await state.set_state(st.ClientResponse.list)

            total_pages = (len(orders) + 5 - 1) // 5  # Общее количество страниц
            await state.update_data(total_order_pages=total_pages)
            await state.update_data(orders_page=1)
            orders = await db.client_available_orders_pagination(message.from_user.id, 1)
            await message.answer(f'<b>Страница 1 из {total_pages}</b>',
                                 reply_markup=await kb.order_total_response_pagination(orders, 1, total_pages))
            await message.answer('Меню 👇',
                             reply_markup=kb.back)
    except Exception:
        await message.answer('Произошла ошибка\n'
                             'Введите команду /start или свяжитесь с @mesudoteach')


@client.callback_query(F.data.startswith('prev-responses-for-order_'), st.ClientResponse.list)
@client.callback_query(F.data.startswith('next-responses-for-order_'), st.ClientResponse.list)
async def responses_for_order_pagination(callback: CallbackQuery, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        await callback.answer('')
        page = int(callback.data.split('_')[1])
        await state.update_data(orders_page=page)
        orders = await db.client_available_orders_pagination(callback.from_user.id, page)
        tdata = await state.get_data()
        total_pages = tdata['total_order_pages']
        await callback.message.edit_text(f'<b>Страница {page} из {total_pages}</b>',
                             reply_markup=await kb.order_total_response_pagination(orders, page, total_pages))
    except Exception:
        await callback.message.answer('Произошла ошибка\n'
                             'Введите команду /start или свяжитесь с @mesudoteach')


@client.callback_query(F.data == 'no_responses', st.ClientResponse.list)
async def no_responses(callback: CallbackQuery):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        # ответ на callback
        await callback.answer('Нет откликов')
    except Exception:
        await callback.message.answer('Произошла ошибка\n'
                                      'Введите команду /start или свяжитесь с @mesudoteach')


@client.callback_query(F.data.startswith('total-order-responses_'), st.ClientResponse.list)
async def client_responses_for_order(callback: CallbackQuery, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        # ответ на callback
        await callback.answer('')
        # устанавливаем нужное FSM состояние
        await state.set_state(st.ClientResponse.order_responses)
        responses = await db.client_responses(callback.data.split('_')[1])

        total_pages = (len(responses) + 5 - 1) // 5  # Общее количество страниц
        await state.update_data(total_pages=total_pages)
        await state.update_data(page=1)
        await state.update_data(select_order=callback.data.split('_')[1])
        responses = await db.client_responses_pagination(callback.data.split('_')[1], 1)
        order = await db.get_order(callback.data.split('_')[1])
        await callback.message.edit_text(f'Отклики для заказа <b>{order.title}</b>\n'
                             f'<b>Страница 1 из {total_pages}</b>',
                             reply_markup=await kb.client_responses_for_order_pagination(responses, 1, total_pages))
    except Exception:
        await callback.message.answer('Произошла ошибка\n'
                                      'Введите команду /start или свяжитесь с @mesudoteach')


@client.callback_query(F.data.startswith('prev-client-response-info_'), st.ClientResponse.order_responses)
@client.callback_query(F.data.startswith('next-client-response-info_'), st.ClientResponse.order_responses)
async def client_response_info_pagination(callback: CallbackQuery, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        await callback.answer('')
        page = int(callback.data.split('_')[1])
        await state.update_data(page=page)
        tdata = await state.get_data()
        order_id = tdata['select_order']
        responses = await db.client_responses_pagination(order_id, page)
        total_pages = tdata['total_pages']
        order = await db.get_order(order_id)
        await callback.message.edit_text(f'Отклики для заказа <b>{order.title}</b>\n'
                                         f'<b>Страница {page} из {total_pages}</b>',
                                         reply_markup=await kb.client_responses_for_order_pagination(responses, page,
                                                                                                     total_pages))
    except Exception:
        await callback.message.answer('Произошла ошибка\n'
                             'Введите команду /start или свяжитесь с @mesudoteach')


@client.callback_query(F.data == 'back_to_total_order_responses', st.ClientResponse.order_responses)
async def back_to_total_order_responses(callback: CallbackQuery, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        # ответ на callback
        await callback.answer('')
        # устанавливаем нужное FSM состояние
        await state.set_state(st.ClientResponse.list)
        tdata = await state.get_data()
        page = tdata['orders_page']
        total_pages = tdata['total_order_pages']
        orders = await db.client_available_orders_pagination(callback.from_user.id, page)
        await callback.message.edit_text(f'<b>Страница {page} из {total_pages}</b>',
                             reply_markup=await kb.order_total_response_pagination(orders, page, total_pages))
    except Exception:
        await callback.message.answer('Произошла ошибка\n'
                                      'Введите команду /start или свяжитесь с @mesudoteach')


@client.callback_query(F.data.startswith('back_'), st.ClientResponse.feedbacks_about_developer)
@client.callback_query(F.data.startswith('client-response-info_'), st.ClientResponse.order_responses)
async def client_response_info(callback: CallbackQuery, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        # ответ на callback
        await callback.answer('')
        await state.update_data(object_id=callback.data.split('_')[1])
        # устанавливаем нужное FSM состояние
        await state.set_state(st.ClientResponse.response_info)
        response = await db.get_response(callback.data.split('_')[1])
        await callback.message.edit_text(f'<b>Разработчик:</b> @{response.developer_rel.username}\n'
                                      f'<b>Рейтинг:</b> {response.developer_rel.rating if response.developer_rel.rating > 0 else 'Нет оценок'}\n'
                                      f'<b>Отклик:</b> {response.description}',
                                      reply_markup=await kb.client_response_menu(response.developer_rel.username, response))
    except Exception:
        await callback.message.answer('Произошла ошибка\n'
                                      'Введите команду /start или свяжитесь с @mesudoteach')


@client.callback_query(F.data == 'hide_client_response_info', st.ClientResponse.response_info)
async def hide_client_response_info(callback: CallbackQuery, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        # ответ на callback
        await callback.answer('')
        await state.set_state(st.ClientResponse.order_responses)
        tdata = await state.get_data()
        order = tdata['select_order']
        page = tdata['page']
        total_pages = tdata['total_pages']
        responses = await db.client_responses_pagination(order, page)
        order = await db.get_order(order)
        await callback.message.edit_text(f'Отклики для заказа <b>{order.title}</b>\n'
                                         f'<b>Страница {page} из {total_pages}</b>',
                                         reply_markup=await kb.client_responses_for_order_pagination(responses, page,
                                                                                                     total_pages))
    except Exception:
        await callback.message.answer('Произошла ошибка\n'
                                      'Введите команду /start или свяжитесь с @mesudoteach')


@client.callback_query(F.data.startswith('the-last-feedbacks-about-developer_'), st.ClientResponse.response_info)
async def the_last_feedbacks_about_developer(callback: CallbackQuery, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        tdata = await state.get_data()
        await state.set_state(st.ClientResponse.feedbacks_about_developer)
        await callback.answer('')
        feedbacks = await db.last_feedbacks_about_developer(callback.data.split('_')[1])
        text = '\n'.join(f'<b>Оценка:</b> {feedback.mark_for_developer}\n'
                         f'<b>Комментарий:</b> {feedback.feedback_about_developer}\n' for feedback in feedbacks)
        await callback.message.edit_text(f'{text}',
                                         reply_markup=await kb.backs(tdata['object_id']))
    except Exception:
        await callback.message.answer('Произошла ошибка\n'
                             'Введите команду /start или свяжитесь с @mesudoteach')


"""--------------------------------Отказ отклика и выбор исполнителя---------------------------------------------"""
@client.callback_query(F.data.startswith('refusal-response_'), st.ClientResponse.response_info)
async def refusal_response(callback: CallbackQuery, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        # ответ на callback
        await callback.answer('')
        await db.refuse_response(callback.data.split('_')[1])
        await state.set_state(st.ClientResponse.order_responses)
        if not await db.is_available_response_for_order(callback.data.split('_')[1]):
            await callback.message.edit_text('Для данного заказа больше нет откликов',
                                             reply_markup=await kb.back_to_total_order_responses())
        else:
            tdata = await state.get_data()
            order_id = tdata['select_order']
            responses = await db.client_responses(order_id)
            total_pages = (len(responses) + 5 - 1) // 5  # Общее количество страниц
            await state.update_data(total_pages=total_pages)
            responses = await db.client_responses_pagination(order_id, 1)
            order = await db.get_order(order_id)
            await callback.message.edit_text(f'Отклики для заказа <b>{order.title}</b>\n'
                                         f'<b>Страница 1 из {total_pages}</b>',
                                         reply_markup=await kb.client_responses_for_order_pagination(responses, 1,
                                                                                                     total_pages))
    except Exception:
        await callback.message.answer('Произошла ошибка\n'
                                      'Введите команду /start или свяжитесь с @mesudoteach')


@client.callback_query(F.data.startswith('choose-response_'), st.ClientResponse.response_info)
async def choose_response(callback: CallbackQuery, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        # ответ на callback
        await callback.answer('')
        # устанавливаем нужное FSM состояние
        await state.set_state(st.ClientResponse.sure_complete_order)
        response = await db.get_response(callback.data.split('_')[1])
        await callback.message.edit_text(f'‼️ Подтвердите, что заказ действительно выполнил разработчик @{response.developer_rel.username}',
                                      reply_markup=await kb.sure_complete_order(callback.data.split('_')[1]))
    except Exception:
        await callback.message.answer('Произошла ошибка\n'
                                      'Введите команду /start или свяжитесь с @mesudoteach')


@client.callback_query(F.data.startswith('cancel-order-complete_'), st.ClientResponse.sure_complete_order)
async def cancel_order_complete(callback: CallbackQuery, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        # ответ на callback
        await callback.answer('')
        # устанавливаем нужное FSM состояние
        await state.set_state(st.ClientResponse.response_info)
        response = await db.get_response(callback.data.split('_')[1])
        await callback.message.edit_text(f'<b>Разработчик:</b> @{response.developer_rel.username}\n'
                                         f'<b>Рейтинг:</b> {response.developer_rel.rating if response.developer_rel.rating > 0 else 'Нет оценок'}\n'
                                         f'<b>Отклик:</b> {response.description}',
                                         reply_markup=await kb.client_response_menu(response.developer_rel.username, response))
    except Exception:
        await callback.message.answer('Произошла ошибка\n'
                                      'Введите команду /start или свяжитесь с @mesudoteach')


@client.callback_query(F.data.startswith('order-complete_'), st.ClientResponse.sure_complete_order)
async def order_complete(callback: CallbackQuery, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    #try:
        # ответ на callback
        await callback.answer('')
        await db.order_complete(callback.data.split('_')[1])
        await state.clear()
        # устанавливаем нужное FSM состояние
        await state.set_state(st.ClientMenu.menu)
        await callback.message.answer('Заказ добавлен в "Историю заказов"', reply_markup=kb.client_main)
    #except Exception:
        #await callback.message.answer('Произошла ошибка\n'
                                      #'Введите команду /start или свяжитесь с @mesudoteach')


"""

Действия в разделе "История заказов"
----------------------------------------------------------------------------------------------
"""
@client.message(F.text == '❌ Отмена', st.ClientCreateFeedback.sure)
@client.message(F.text == '❌ Отмена', st.ClientCreateFeedback.feedback)
@client.message(F.text == '❌ Отмена', st.ClientCreateFeedback.mark)
@client.message(F.text == '⏳ История заказов', st.ClientMenu.menu)
async def order_history(message: Message, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        orders = await db.order_history(message.from_user.id)
        if not orders:
            # устанавливаем нужное FSM состояние
            await state.set_state(st.OrderHistory.list)
            await message.answer('Нет заказов',
                                 reply_markup=kb.back)
        else:
            total_pages = (len(orders) + 5 - 1) // 5  # Общее количество страниц
            await state.update_data(total_pages=total_pages)
            await state.update_data(page=1)
            # устанавливаем нужное FSM состояние
            await state.set_state(st.OrderHistory.list)
            orders = await db.order_history_pagination(message.from_user.id ,1)
            await message.answer(f'<b>Страница 1 из {total_pages}</b>',
                                 reply_markup=await kb.client_history_orders(orders, 1, total_pages))
        await message.answer('Меню 👇',
                             reply_markup=kb.back)
    except Exception:
        await message.answer('Произошла ошибка\n'
                             'Введите команду /start или свяжитесь с @mesudoteach')


@client.callback_query(F.data.startswith('prev-client-history-order_'), st.OrderHistory.list)
@client.callback_query(F.data.startswith('next-client-history-order_'), st.OrderHistory.list)
async def client_history_order_pagination(callback: CallbackQuery, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        await callback.answer('')
        page = int(callback.data.split('_')[1])
        await state.update_data(page=page)
        orders = await db.order_history_pagination(callback.from_user.id ,page)
        tdata = await state.get_data()
        total_pages = tdata['total_pages']
        await callback.message.edit_text(f'<b>Страница {page} из {total_pages}</b>',
                             reply_markup=await kb.client_history_orders(orders, page, total_pages))
    except Exception:
        await callback.message.answer('Произошла ошибка\n'
                             'Введите команду /start или свяжитесь с @mesudoteach')


@client.callback_query(F.data.startswith('history-order_'), st.OrderHistory.list)
async def history_order(callback: CallbackQuery, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        # ответ на callback
        await callback.answer('Подробности заказа')
        # устанавливаем нужное FSM состояние
        await state.set_state(st.OrderHistory.order_info)
        # извлекаем из callback id запроса
        order_info = await db.get_completed_order(callback.data.split('_')[1])
        await callback.message.edit_text(f'<b>Заказ</b>: {order_info.title}\n'
                                         f'<b>Исполнитель</b>: @{order_info.developer_rel.username}\n\n'
                                         f'<b>Ваша оценка:</b>  {order_info.mark_for_developer 
                                         if order_info.mark_for_developer else 'Не оценено'}\n'
                                         f'<b>Ваш комментарий:</b> {order_info.feedback_about_developer 
                                         if order_info.feedback_about_developer else 'Нет комментария'}\n\n'
                                         f'<b>Оценка исполнителя:</b>  {order_info.mark_for_client 
                                         if order_info.mark_for_client else 'Не оценено'}\n'
                                         f'<b>Комментарий исполнителя:</b> {order_info.feedback_about_client 
                                         if order_info.feedback_about_client else 'Нет комментария'}\n\n'
                                         f'<b>Дата</b>: {order_info.date.strftime('%d.%m.%Y')}\n\n',
                                         reply_markup=await kb.history_order_info(order_info))
    except Exception:
        await callback.message.answer('Произошла ошибка\n'
                             'Введите команду /start или свяжитесь с @mesudoteach')


@client.callback_query(F.data == 'hide_history_order_info', st.OrderHistory.order_info)
async def hide_history_order_info(callback: CallbackQuery, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        # ответ на callback
        await callback.answer('')
        await state.set_state(st.OrderHistory.list)
        tdata = await state.get_data()
        page = tdata['page']
        total_pages = tdata['total_pages']
        orders = await db.order_history_pagination(callback.from_user.id, page)
        await callback.message.edit_text(f'<b>Страница {page} из {total_pages}</b>',
                             reply_markup=await kb.client_history_orders(orders, page, total_pages))
    except Exception:
        await callback.message.answer('Произошла ошибка\n'
                                      'Введите команду /start или свяжитесь с @mesudoteach')


"""--------------------------------Добавление отзыва---------------------------------------------"""
@client.callback_query(F.data.startswith('client-create-feedback_'), st.OrderHistory.order_info)
async def client_create_feedback_mark(callback: CallbackQuery, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        # ответ на callback
        await callback.answer('')
        await state.update_data(select_order=callback.data.split('_')[1])
        # устанавливаем нужное FSM состояние
        await state.set_state(st.ClientCreateFeedback.mark)
        await callback.message.answer('Оцените работу исполнителя (от 1 до 5)', reply_markup=kb.cancel)
    except Exception:
        await callback.message.answer('Произошла ошибка\n'
                                      'Введите команду /start или свяжитесь с @mesudoteach')


@client.message(st.ClientCreateFeedback.mark)
async def client_create_feedback_feedback(message: Message, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        if message.text not in ['1', '2', '3', '4', '5']:
            await message.answer('Введённое вами значение некорректно\n'
                                 'Оцените работу исполнителя (от 1 до 5)')
        else:
            # записываем в нужное нам состояние введённую информацию
            await state.update_data(mark=message.text)
            # устанавливаем нужное FSM состояние
            await state.set_state(st.ClientCreateFeedback.feedback)
            await message.answer('Напишите свой отзыв (до 1000 символов)')
    except Exception:
        await message.answer('Произошла ошибка\n'
                             'Введите команду /start или свяжитесь с @mesudoteach')


@client.message(st.ClientCreateFeedback.feedback)
async def sure_client_create_feedback(message: Message, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        if len(message.text) > 10000:
            await message.answer('Отзыв не должен быть более 1000 символов')
        else:
            # записываем в нужное нам состояние введённую информацию
            await state.update_data(feedback=message.text)
            # берём данные из всех состояний
            tdata = await state.get_data()
            # устанавливаем нужное FSM состояние
            await state.set_state(st.ClientCreateFeedback.sure)
            order = await db.get_completed_order(tdata['select_order'])
            await message.answer(f'Подтвердите, что вы хотите создать следующий отзыв?\n\n'
                                 f'<b>Заказ:</b> {order.title}\n'
                                 f'<b>Оценка:</b> {tdata['mark']}\n'
                                 f'<b>Комментарий:</b> {tdata['feedback']}',
                                 reply_markup=kb.sure)
    except Exception:
        await message.answer('Произошла ошибка\n'
                             'Введите команду /start или свяжитесь с @mesudoteach')


@client.message(F.text == '🌟 Да', st.ClientCreateFeedback.sure)
async def ok_client_create_feedback(message: Message, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        # берём данные из всех состояний
        tdata = await state.get_data()
        order = await db.get_completed_order(tdata['select_order'])
        total_feedbacks_about_developer = await db.feedbacks_about_developer(order.developer)
        mark_sum_about_developer = sum(feedback.mark_for_developer for feedback in total_feedbacks_about_developer)
        total_feedbacks_about_developer = len(total_feedbacks_about_developer)
        # добавляем новый отзыв в БД
        await db.add_client_feedback(tdata['select_order'], tdata['mark'],
                                     tdata['feedback'], total_feedbacks_about_developer, mark_sum_about_developer)
        orders = await db.order_history(message.from_user.id)
        total_pages = (len(orders) + 5 - 1) // 5  # Общее количество страниц
        await state.update_data(total_pages=total_pages)
        await state.update_data(page=1)
        # устанавливаем нужное FSM состояние
        await state.set_state(st.OrderHistory.list)
        orders = await db.order_history_pagination(message.from_user.id, 1)
        await message.answer(f'<b>Страница 1 из {total_pages}</b>',
                             reply_markup=await kb.client_history_orders(orders, 1, total_pages))
        await message.answer('Меню 👇',
                            reply_markup=kb.back)
    except Exception:
        await message.answer('Произошла ошибка\n'
                             'Введите команду /start или свяжитесь с @mesudoteach')


"""--------------------------------Изменение отзыва---------------------------------------------"""
@client.callback_query(F.data.startswith('client-edit-feedback_'), st.OrderHistory.order_info)
async def client_edit_feedback_mark(callback: CallbackQuery, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        # ответ на callback
        await callback.answer('')
        await state.update_data(select_order=callback.data.split('_')[1])
        # устанавливаем нужное FSM состояние
        await state.set_state(st.ClientEditFeedback.mark)
        await callback.message.answer('Новая оценка (от 1 до 5)', reply_markup=kb.cancel)
    except Exception:
        await callback.message.answer('Произошла ошибка\n'
                                      'Введите команду /start или свяжитесь с @mesudoteach')


@client.message(st.ClientEditFeedback.mark)
async def client_edit_feedback_feedback(message: Message, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        if message.text not in ['1', '2', '3', '4', '5']:
            await message.answer('Введённое вами значение некорректно\n'
                                 'Введите новую оценку (от 1 до 5)')
        else:
            # записываем в нужное нам состояние введённую информацию
            await state.update_data(mark=message.text)
            # устанавливаем нужное FSM состояние
            await state.set_state(st.ClientEditFeedback.feedback)
            await message.answer('Напишите новый отзыв (до 1000 символов)')
    except Exception:
        await message.answer('Произошла ошибка\n'
                             'Введите команду /start или свяжитесь с @mesudoteach')


@client.message(st.ClientEditFeedback.feedback)
async def sure_client_edit_feedback(message: Message, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        if len(message.text) > 10000:
            await message.answer('Отзыв не должен быть более 1000 символов')
        else:
            # записываем в нужное нам состояние введённую информацию
            await state.update_data(feedback=message.text)
            # берём данные из всех состояний
            tdata = await state.get_data()
            # устанавливаем нужное FSM состояние
            await state.set_state(st.ClientEditFeedback.sure)
            order = await db.get_completed_order(tdata['select_order'])
            await message.answer(f'Подтвердите, что вы хотите внести следующие изменения в отзыв?\n\n'
                                 f'<b>Заказ:</b> {order.title}\n'
                                 f'<b>Оценка:</b> {tdata['mark']}\n'
                                 f'<b>Комментарий:</b> {tdata['feedback']}',
                                 reply_markup=kb.sure)
    except Exception:
        await message.answer('Произошла ошибка\n'
                             'Введите команду /start или свяжитесь с @mesudoteach')


@client.message(F.text == '🌟 Да', st.ClientEditFeedback.sure)
async def ok_client_edit_feedback(message: Message, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        # берём данные из всех состояний
        tdata = await state.get_data()
        order = await db.get_completed_order(tdata['select_order'])
        total_feedbacks_about_developer = await db.feedbacks_about_developer(order.developer)
        mark_sum_about_developer = sum(feedback.mark_for_developer for feedback in total_feedbacks_about_developer)
        total_feedbacks_about_developer = len(total_feedbacks_about_developer)
        # добавляем новый отзыв в БД
        await db.edit_client_feedback(tdata['select_order'], tdata['mark'],
                                     tdata['feedback'], total_feedbacks_about_developer, mark_sum_about_developer)
        orders = await db.order_history(message.from_user.id)
        total_pages = (len(orders) + 5 - 1) // 5  # Общее количество страниц
        await state.update_data(total_pages=total_pages)
        await state.update_data(page=1)
        # устанавливаем нужное FSM состояние
        await state.set_state(st.OrderHistory.list)
        orders = await db.order_history_pagination(message.from_user.id, 1)
        await message.answer(f'<b>Страница 1 из {total_pages}</b>',
                             reply_markup=await kb.client_history_orders(orders, 1, total_pages))
        await message.answer('Меню 👇',
                            reply_markup=kb.back)
    except Exception:
        await message.answer('Произошла ошибка\n'
                             'Введите команду /start или свяжитесь с @mesudoteach')


"""

Действия в разделе "Мой профиль"
----------------------------------------------------------------------------------------------
"""
@client.message(F.text == '😁 Мой профиль', st.ClientMenu.menu)
async def client_profile(message: Message, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        # устанавливаем нужное FSM состояние
        await state.set_state(st.ClientProfile.profile)
        client_info = await db.get_client(message.from_user.id)
        await message.answer(f'<b>Рейтинг:</b> {client_info.rating if client_info.rating > 0 else 'Нет оценок'}\n'
                             f'<b>Количество выполненных заказов:</b> {client_info.completed_orders}\n',
                                 reply_markup= kb.back)
    except Exception:
        await message.answer('Произошла ошибка\n'
                             'Введите команду /start или свяжитесь с @mesudoteach')


"""

Действия в разделе "FAQ"
----------------------------------------------------------------------------------------------
"""
@client.message(F.text == '💎 FAQ', st.ClientMenu.menu)
async def client_faq(message: Message, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        # устанавливаем нужное FSM состояние
        await state.set_state(st.FAQ.client)
        await message.answer('Часто задаваемые вопросы 👇 \n https://telegra.ph/',
                                 reply_markup=kb.back)
    except Exception:
        await message.answer('Произошла ошибка\n'
                             'Введите команду /start или свяжитесь с @mesudoteach')


"""

Чтение сообщений из закрытого чата (модерация)
----------------------------------------------------------------------------------------------

"""


@client.callback_query(lambda callback: callback.message.chat.id == ADMIN_ORDER_CHAT_ID, F.data.startswith('moderation-passed_'))  # хэндлер срабатывает только тогда, когда в нужный чат присылается сообщение
async def moderation_passed(callback: CallbackQuery, bot: Bot):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    #try:
        # ответ на callback
        await callback.answer('Спасибо за работу')
        await callback.message.delete()
        # извлекаем из callback id запроса
        order = await db.available_order(callback.data.split('_')[1])
        await bot.send_message(chat_id=order.client, text='<b>‼️ Ваш заказ прошёл модерацию</b>')
    #except Exception:
        #await callback.message.answer('Произошла ошибка\n'
                             #'Введите команду /start или свяжитесь с @mesudoteach')


@client.callback_query(lambda callback: callback.message.chat.id == ADMIN_ORDER_CHAT_ID, F.data.startswith('moderation-failed_'))  # хэндлер срабатывает только тогда, когда в нужный чат присылается сообщение
async def moderation_failed(callback: CallbackQuery, bot: Bot):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    #try:
        # ответ на callback
        await callback.answer('Спасибо за работу')
        await callback.message.delete()
        # извлекаем из callback id запроса
        order = await db.delete_order(callback.data.split('_')[1])
        await bot.send_message(chat_id=order.client, text='<b>‼️ Ваш заказ не прошёл модерацию</b>')
    #except Exception:
        #await callback.message.answer('Произошла ошибка\n'
                             #'Введите команду /start или свяжитесь с @mesudoteach')