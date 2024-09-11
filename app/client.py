
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext

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
async def client_order_info(callback: Message, state: FSMContext):
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
@client.message(F.text == '➕ Создать заказ', st.ClientOrder.list)
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
async def no_responses(callback: Message, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        # ответ на callback
        await callback.answer('Нет откликов')
    except Exception:
        await callback.message.answer('Произошла ошибка\n'
                                      'Введите команду /start или свяжитесь с @kosdem04')


@client.callback_query(F.data.startswith('total-order-responses_'), st.ClientResponse.list)
async def client_response_info(callback: Message, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        # ответ на callback
        await callback.answer('')
        # устанавливаем нужное FSM состояние
        await state.set_state(st.ClientResponse.order_responses)
        # записываем в нужное нам состояние введённую информацию
        #await state.update_data(order=callback.data.split('_')[1])
        responses = await db.client_responses(callback.data.split('_')[1])
        for response in responses:
            developer = await db.get_developer(response.developer)
            await callback.message.answer(f'<b>Разработчик</b>: @{developer.username}\n'
                                          f'<b>Отклик</b>:\n{response.description}',
                                          reply_markup=await kb.client_response_menu(developer.username, response.id))
    except Exception:
        await callback.message.answer('Произошла ошибка\n'
                                      'Введите команду /start или свяжитесь с @kosdem04')


@client.callback_query(F.data.startswith('refusal-response_'), st.ClientResponse.order_responses)
async def refusal_response(callback: Message, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        # ответ на callback
        await callback.answer('')
        await callback.message.delete()
        await db.refuse_response(callback.data.split('_')[1])
    except Exception:
        await callback.message.answer('Произошла ошибка\n'
                                      'Введите команду /start или свяжитесь с @kosdem04')


@client.callback_query(F.data.startswith('choose-response_'), st.ClientResponse.order_responses)
async def choose_response(callback: Message, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        # ответ на callback
        await callback.answer('')
        # устанавливаем нужное FSM состояние
        await state.set_state(st.ClientResponse.sure_complete_order)
        await state.update_data(sure_complete_order=callback.data.split('_')[1])
        response = await db.get_response(callback.data.split('_')[1])
        developer = await db.get_developer(response.developer)
        await callback.message.answer(f'‼️ Подтвердите, что заказ действительно выполнил разработчик @{developer.username}',
                                      reply_markup=kb.sure)
    except Exception:
        await callback.message.answer('Произошла ошибка\n'
                                      'Введите команду /start или свяжитесь с @kosdem04')


@client.message(F.text == '❌ Отмена', st.ClientResponse.sure_complete_order)
async def cancel_choose_response(message: Message, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        # устанавливаем нужное FSM состояние
        await state.set_state(st.ClientResponse.order_responses)
        await callbackmessage.answer('Меню 👇',
                             reply_markup=kb.back)
    except Exception:
        await callback.message.answer('Произошла ошибка\n'
                                      'Введите команду /start или свяжитесь с @kosdem04')


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
async def moderation_passed(callback: Message, bot: Bot):
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
async def moderation_failed(callback: Message, bot: Bot):
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