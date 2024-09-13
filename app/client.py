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


@client.message(F.text == '◀️ Назад', st.ClientFeedback.list)
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
        # устанавливаем нужное FSM состояние
        await state.set_state(st.ClientOrder.list)
        orders = await db.client_orders(message.from_user.id)
        if not orders:
            await message.answer('У вас нет ни одного активного заказа',
                                 reply_markup=kb.create_and_back)
        else:
            await message.answer('Ваши заказы',
                                 reply_markup= await kb.client_orders(orders))
            await message.answer('Меню 👇',
                                 reply_markup=kb.create_and_back)
    except Exception:
        await message.answer('Произошла ошибка\n'
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
        await callback.message.answer('Подробности заказа 🔹')
        await callback.message.answer(f'<b>Название</b>: {order_info.title}\n'
                             f'<b>Описание</b>:\n{order_info.description}',
                             reply_markup=kb.client_order_menu)
    except Exception:
        await callback.message.answer('Произошла ошибка\n'
                                      'Введите команду /start или свяжитесь с @kosdem04')


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
                                                           f'<b>Название:</b> {tdata['title']}\n'
                                                           f'<b>Описание:</b>\n{tdata['description']}\n',
                               reply_markup=await kb.order_moderation(order.id))
        # устанавливаем нужное FSM состояние
        await state.set_state(st.ClientOrder.list)
        orders = await db.client_orders(message.from_user.id)
        await message.answer('‼️ Ваш заказ отправлен на модерацию')
        if not orders:
            await message.answer('У вас нет ни одного активного заказа',
                                 reply_markup=kb.create_and_back)
        else:
            await message.answer('Ваши заказы',
                                 reply_markup=await kb.client_orders(orders))
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
            await message.answer(f'Вы уверены, что хотите данные заказа на следующие?\n\n'
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
        # устанавливаем нужное FSM состояние
        await state.set_state(st.ClientOrder.list)
        orders = await db.client_orders(message.from_user.id)
        if not orders:
            await message.answer('У вас нет ни одного активного заказа',
                                 reply_markup=kb.create_and_back)
        else:
            await message.answer('Ваши заказы',
                                 reply_markup=await kb.client_orders(orders))
            await message.answer('Меню 👇',
                                 reply_markup=kb.back)
    except Exception:
        await message.answer('Произошла ошибка\n'
                             'Введите команду /start или свяжитесь с @mesudoteach')


"""

Действия в разделе "Отклики"
----------------------------------------------------------------------------------------------
"""
@client.message(F.text == '◀️ Назад', st.ClientResponse.order_responses)
@client.message(F.text == '💥 Отклики', st.ClientMenu.menu)
async def client_response_list(message: Message, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        # устанавливаем нужное FSM состояние
        await state.set_state(st.ClientResponse.list)
        orders = await db.client_orders(message.from_user.id)
        if not orders:
            await message.answer('Нужен хотя бы один активный заказ',
                                 reply_markup=kb.create_and_back)
        else:
            for order in orders:
                total_response = await db.total_response(order.id)
                await message.answer(f'<b>Заказ:</b> {order.title}',
                                     reply_markup= await kb.order_total_response(order.id, total_response))
            await message.answer('Меню 👇',
                                 reply_markup=kb.back)
    except Exception:
        await message.answer('Произошла ошибка\n'
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
                                      'Введите команду /start или свяжитесь с @kosdem04')


@client.callback_query(F.data.startswith('total-order-responses_'), st.ClientResponse.list)
async def client_response_info(callback: CallbackQuery, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        # ответ на callback
        await callback.answer('')
        # устанавливаем нужное FSM состояние
        await state.set_state(st.ClientResponse.order_responses)
        responses = await db.client_responses(callback.data.split('_')[1])
        order = await db.get_order(callback.data.split('_')[1])
        await callback.message.answer(f'Отклики для заказа <b>{order.title}</b>')
        for response in responses:
            developer = await db.get_developer(response.developer)
            await callback.message.answer(f'<b>Разработчик:</b> @{developer.username}\n'
                                          f'<b>Рейтинг:</b> {developer.rating if developer.rating > 0 else 'Нет оценок'}\n'
                                          f'<b>Отклик:</b> {response.description}',
                                          reply_markup=await kb.client_response_menu(developer.username, response.id))
    except Exception:
        await callback.message.answer('Произошла ошибка\n'
                                      'Введите команду /start или свяжитесь с @kosdem04')


@client.callback_query(F.data.startswith('refusal-response_'), st.ClientResponse.order_responses)
async def refusal_response(callback: CallbackQuery):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        # ответ на callback
        await callback.answer('')
        await callback.message.delete()
        await db.refuse_response(callback.data.split('_')[1])
        if not await db.is_available_response_for_order(callback.data.split('_')[1]):
            await callback.message.answer('Для данного заказа больше нет откликов')
    except Exception:
        await callback.message.answer('Произошла ошибка\n'
                                      'Введите команду /start или свяжитесь с @kosdem04')


@client.callback_query(F.data.startswith('choose-response_'), st.ClientResponse.order_responses)
async def choose_response(callback: CallbackQuery, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        # ответ на callback
        await callback.answer('')
        # устанавливаем нужное FSM состояние
        await state.set_state(st.ClientResponse.sure_complete_order)
        response = await db.get_response(callback.data.split('_')[1])
        developer = await db.get_developer(response.developer)
        await callback.message.edit_text(f'‼️ Подтвердите, что заказ действительно выполнил разработчик @{developer.username}',
                                      reply_markup=await kb.sure_complete_order(callback.data.split('_')[1]))
    except Exception:
        await callback.message.answer('Произошла ошибка\n'
                                      'Введите команду /start или свяжитесь с @kosdem04')


@client.callback_query(F.data.startswith('cancel-order-complete_'), st.ClientResponse.sure_complete_order)
async def cancel_order_complete(callback: CallbackQuery, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        # ответ на callback
        await callback.answer('')
        # устанавливаем нужное FSM состояние
        await state.set_state(st.ClientResponse.order_responses)
        response = await db.get_response(callback.data.split('_')[1])
        developer = await db.get_developer(response.developer)
        await callback.message.edit_text(f'<b>Разработчик</b>: @{developer.username}\n'
                                          f'<b>Отклик</b>:\n{response.description}',
                                          reply_markup=await kb.client_response_menu(developer.username, response.id))
    except Exception:
        await callback.message.answer('Произошла ошибка\n'
                                      'Введите команду /start или свяжитесь с @kosdem04')



@client.callback_query(F.data.startswith('order-complete_'), st.ClientResponse.sure_complete_order)
async def order_complete(callback: CallbackQuery, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        # ответ на callback
        await callback.answer('')
        await db.order_complete(callback.data.split('_')[1])
        await state.clear()
        # устанавливаем нужное FSM состояние
        await state.set_state(st.ClientMenu.menu)
        await callback.message.answer('Заказ добавлен в "Историю заказов"', reply_markup=kb.client_main)
    except Exception:
        await callback.message.answer('Произошла ошибка\n'
                                      'Введите команду /start или свяжитесь с @kosdem04')


"""

Действия в разделе "История заказов"
----------------------------------------------------------------------------------------------
"""
@client.message(F.text == '⏳ История заказов', st.ClientMenu.menu)
async def order_history(message: Message, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        # устанавливаем нужное FSM состояние
        await state.set_state(st.OrderHistory.list)
        orders = await db.order_history(message.from_user.id)
        if not orders:
            await message.answer('Нет заказов',
                                 reply_markup=kb.back)
        else:
            for order in orders:
                developer = await db.get_developer(order.developer)
                await message.answer(f'<b>Заказ:</b> {order.title}\n'
                                     f'<b>Исполнитель:</b> @{developer.username}\n'
                                     f'<b>Дата:</b> {order.date.strftime('%d.%m.%Y')}\n',)
            await message.answer('Меню 👇',
                                 reply_markup=kb.back)
    except Exception:
        await message.answer('Произошла ошибка\n')



"""

Действия в разделе "Отзывы"
----------------------------------------------------------------------------------------------
"""
@client.message(F.text == '❌ Отмена', st.ClientCreateFeedback.sure)
@client.message(F.text == '❌ Отмена', st.ClientCreateFeedback.feedback)
@client.message(F.text == '❌ Отмена', st.ClientCreateFeedback.mark)
@client.message(F.text == '❌ Отмена', st.ClientCreateFeedback.select_order)
@client.message(F.text == '⭐️ Отзывы', st.ClientMenu.menu)
async def client_feedbacks(message: Message, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        # устанавливаем нужное FSM состояние
        await state.set_state(st.ClientFeedback.list)
        feedbacks = await db.client_feedbacks(message.from_user.id)
        if not feedbacks:
            await message.answer('Вы не написали ни одного отзыва',
                                 reply_markup=kb.create_and_back)
        else:
            await message.answer('Ваши отзывы')
            for feedback in feedbacks:
                developer = await db.get_developer(feedback.developer)
                await message.answer(f'<b>Заказ:</b> {feedback.title}\n'
                                     f'<b>Исполнитель:</b> @{developer.username}\n'
                                     f'<b>Ваша оценка:</b>  {feedback.mark_for_developer}\n'
                                     f'<b>Ваш комментарий:</b>  {feedback.feedback_about_developer}\n'
                                     f'<b>Дата:</b> {feedback.date.strftime('%d.%m.%Y')}\n')
            await message.answer('Меню 👇',
                                 reply_markup=kb.create_and_back)
    except Exception:
        await message.answer('Произошла ошибка\n'
                             'Введите команду /start или свяжитесь с @mesudoteach')


"""-------------------------------------------Создать отзыв---------------------------------------------------"""
@client.message(F.text == '➕ Создать', st.ClientFeedback.list)
async def client_create_feedback_select_order(message: Message, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        orders = await db.orders_without_feedback_about_developer(message.from_user.id)
        if not orders:
            await message.answer('Вы написали отзывы для всех Ваших заказов или у Вас нет выполненных заказов',
                                 reply_markup=kb.back)
        else:
            # устанавливаем нужное FSM состояние
            await state.set_state(st.ClientCreateFeedback.select_order)
            await message.answer(f'Выберите заказ, который хотите оценить:',
                                 reply_markup=await kb.orders_without_feedback_about_developer(orders))
            await message.answer('Меню 👇',
                                 reply_markup=kb.cancel)
    except Exception:
        await message.answer('Произошла ошибка\n'
                             'Введите команду /start или свяжитесь с @mesudoteach')


@client.callback_query(F.data.startswith('order-for-create-feedback_'), st.ClientCreateFeedback.select_order)
async def client_create_feedback_mark(callback: CallbackQuery, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        # ответ на callback
        await callback.answer('')
        await state.update_data(select_order=callback.data.split('_')[1])
        # устанавливаем нужное FSM состояние
        await state.set_state(st.ClientCreateFeedback.mark)
        await callback.message.answer('Оцените работу исполнителя (от 1 до 5)')
    except Exception:
        await callback.message.answer('Произошла ошибка\n'
                                      'Введите команду /start или свяжитесь с @kosdem04')


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
    #try:
        # берём данные из всех состояний
        tdata = await state.get_data()
        order = await db.get_completed_order(tdata['select_order'])
        total_feedbacks_about_developer = await db.feedbacks_about_developer(order.developer)
        total_feedbacks_about_developer = len(total_feedbacks_about_developer)
        # добавляем новый отзыв в БД
        await db.add_client_feedback(tdata['select_order'], tdata['mark'],
                                     tdata['feedback'], total_feedbacks_about_developer)
        # устанавливаем нужное FSM состояние
        await state.set_state(st.ClientFeedback.list)
        feedbacks = await db.client_feedbacks(message.from_user.id)
        if not feedbacks:
            await message.answer('Вы не написали ни одного отзыва',
                                 reply_markup=kb.create_and_back)
        else:
            await message.answer('Ваши отзывы')
            for feedback in feedbacks:
                developer = await db.get_developer(feedback.developer)
                await message.answer(f'<b>Заказ:</b> {feedback.title}\n'
                                     f'<b>Исполнитель:</b> @{developer.username}\n'
                                     f'<b>Ваша оценка:</b>  {feedback.mark_for_developer}\n'
                                     f'<b>Ваш комментарий:</b>  {feedback.feedback_about_developer}\n'
                                     f'<b>Дата:</b> {feedback.date.strftime('%d.%m.%Y')}\n')
            await message.answer('Меню 👇',
                                 reply_markup=kb.create_and_back)
    #except Exception:
        #await message.answer('Произошла ошибка\n'
                             #'Введите команду /start или свяжитесь с @mesudoteach')


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
        await message.answer('Часто задаваемые вопросы',
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
    try:
        # ответ на callback
        await callback.answer('Спасибо за работу')
        await callback.message.delete()
        # извлекаем из callback id запроса
        order = await db.available_order(callback.data.split('_')[1])
        await bot.send_message(chat_id=order.client, text='<b>‼️ Ваш заказ прошёл модерацию</b>')
    except Exception:
        await callback.message.answer('Произошла ошибка\n'
                             'Введите команду /start или свяжитесь с @mesudoteach')


@client.callback_query(lambda callback: callback.message.chat.id == ADMIN_ORDER_CHAT_ID, F.data.startswith('moderation-failed_'))  # хэндлер срабатывает только тогда, когда в нужный чат присылается сообщение
async def moderation_failed(callback: CallbackQuery, bot: Bot):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        # ответ на callback
        await callback.answer('Спасибо за работу')
        await callback.message.delete()
        # извлекаем из callback id запроса
        order = await db.delete_order(callback.data.split('_')[1])
        await bot.send_message(chat_id=order.client, text='<b>‼️ Ваш заказ не прошёл модерацию</b>')
    except Exception:
        await callback.message.answer('Произошла ошибка\n'
                             'Введите команду /start или свяжитесь с @mesudoteach')