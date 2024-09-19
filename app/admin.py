from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Filter, CommandStart, Command
from config import ADMINS
import app.keyboards as kb
import app.database.requests as db
import app.states as st

admin = Router()


class AdminProtect(Filter):
    def __init__(self):
        self.admins = ADMINS

    async def __call__(self, message: Message):
        return message.from_user.id in self.admins
    

"""

Главное меню админ-панели
----------------------------------------------------------------------------------------------
"""
@admin.message(F.text == '❌ Отмена', st.SendAll.sure)
@admin.message(F.text == '❌ Отмена', st.SendAll.message)
@admin.message(F.text == '❌ Отмена', st.SendAll.select_method)
@admin.message(AdminProtect(), F.text == '◀️ Назад', st.AdminTariff.all_tariffs)
@admin.message(AdminProtect(), Command('admin_panel'))
async def admin_panel(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(st.AdminMenu.menu)
    # отправляем администратору сообщение, reply_markup — параметр с нужной клавиатурой
    await message.answer('Админ-панель', reply_markup=kb.admin_panel)


@admin.message(AdminProtect(), F.text == '◀️ Выйти', st.AdminMenu.menu)
async def back_admin_panel(message: Message, state: FSMContext):
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

Действия в разделе "Тарифы"
----------------------------------------------------------------------------------------------
"""
@admin.message(F.text == '❌ Отмена', st.EditTariff.sure)
@admin.message(F.text == '❌ Отмена', st.EditTariff.amount)
@admin.message(F.text == '❌ Отмена', st.EditTariff.responses)
@admin.message(F.text == '❌ Отмена', st.EditTariff.description)
@admin.message(F.text == '❌ Отмена', st.EditTariff.name)
@admin.message(F.text == '❌ Отмена', st.AddTariff.sure)
@admin.message(F.text == '❌ Отмена', st.AddTariff.amount)
@admin.message(F.text == '❌ Отмена', st.AddTariff.responses)
@admin.message(F.text == '❌ Отмена', st.AddTariff.description)
@admin.message(F.text == '❌ Отмена', st.AddTariff.name)
@admin.message(AdminProtect(), F.text == '🤖 Тарифы', st.AdminMenu.menu)
async def admin_statistic(message: Message, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        # устанавливаем нужное FSM состояние
        await state.set_state(st.AdminTariff.all_tariffs)
        # берём из БД статистику финансов пользователя
        tariffs = await db.all_tariffs()
        if not tariffs:
            await message.answer('Нет ни одного тарифа',
                                 reply_markup=kb.tariffs_menu)
        else:
            for tariff in tariffs:
                await message.answer(f'<b>Название:</b> {tariff.name}\n'
                                     f'<b>Описание:</b> {tariff.description}\n\n'
                                     f'<b>Откликов в день:</b> {tariff.responses}\n'
                                     f'<b>Стоимость:</b> {tariff.amount}₽',
                                     reply_markup=await kb.tariff_menu(tariff))
            await message.answer('Меню 👇',
                                 reply_markup=kb.tariffs_menu)
    except Exception:
        await message.answer('Произошла ошибка\n'
                             'Введите команду /start или свяжитесь с @mesudoteach')


"""-------------------------------------------Добавить тариф---------------------------------------------------"""
@admin.message(F.text == '➕ Добавить тариф', st.AdminTariff.all_tariffs)
async def tariff_name(message: Message, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        # устанавливаем нужное FSM состояние
        await state.set_state(st.AddTariff.name)
        await message.answer('Введите название для нового тарифа (до 25 символов)',
                             reply_markup=kb.cancel)
    except Exception:
        await message.answer('Произошла ошибка\n'
                             'Введите команду /start или свяжитесь с @mesudoteach')


@admin.message(st.AddTariff.name)
async def tariff_description(message: Message, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        if len(message.text) > 25:
            await message.answer('Название тарифа не должно быть более 25 символов',
                                 reply_markup=kb.cancel)
        else:
            # записываем в нужное нам состояние введённую информацию
            await state.update_data(name=message.text)
            # устанавливаем нужное FSM состояние
            await state.set_state(st.AddTariff.description)
            await message.answer('Введите описание тарифа',
                                 reply_markup=kb.cancel)
    except Exception:
        await message.answer('Произошла ошибка\n'
                             'Введите команду /start или свяжитесь с @mesudoteach')


@admin.message(st.AddTariff.description)
async def tariff_responses(message: Message, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        if len(message.text) > 10000:
            await message.answer('Описание тарифа не должно быть более 1000 символов',
                                 reply_markup=kb.cancel)
        else:
            # записываем в нужное нам состояние введённую информацию
            await state.update_data(description=message.text)

            # устанавливаем нужное FSM состояние
            await state.set_state(st.AddTariff.responses)
            await message.answer('Введите количество доступных в день откликов по этому тарифу',
                                 reply_markup=kb.cancel)
    except Exception:
        await message.answer('Произошла ошибка\n'
                             'Введите команду /start или свяжитесь с @mesudoteach')


@admin.message(st.AddTariff.responses)
async def tariff_amount(message: Message, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        if message.text.isdigit() and not message.text.isalpha():
            # записываем в нужное нам состояние введённую информацию
            await state.update_data(responses=int(message.text))
            # устанавливаем нужное FSM состояние
            await state.set_state(st.AddTariff.amount)
            await message.answer('Введите стоимость нового тарифа в рублях',
                                 reply_markup=kb.cancel)
        else:
            await message.answer('Введено некорректное значение\n'
                                 'Введите количество доступных в день откликов по этому тарифу',
                                 reply_markup=kb.cancel)
    except Exception:
        await message.answer('Произошла ошибка\n'
                             'Введите команду /start или свяжитесь с @mesudoteach')


@admin.message(st.AddTariff.amount)
async def sure_add_tariff(message: Message, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        if message.text.isdigit() and not message.text.isalpha():
            # записываем в нужное нам состояние введённую информацию
            await state.update_data(amount=int(message.text))
            # устанавливаем нужное FSM состояние
            await state.set_state(st.AddTariff.sure)
            tdata = await state.get_data()
            await message.answer(f'Вы уверены, что хотите добавить тариф со следующими данными?\n\n'
                                 f'<b>Название</b>: {tdata['name']}\n'
                                 f'<b>Описание</b>: {tdata['description']}\n\n'
                                 f'<b>Откликов в день</b>: {tdata['responses']}\n'
                                 f'<b>Стоимость</b>: {tdata['amount']}₽',
                                 reply_markup=kb.sure)
        else:
            await message.answer('Введено некорректное значение\n'
                                 'Введите стоимость нового тарифа в рублях',
                                 reply_markup=kb.cancel)
    except Exception:
        await message.answer('Произошла ошибка\n'
                             'Введите команду /start или свяжитесь с @mesudoteach')


@admin.message(F.text == '🌟 Да', st.AddTariff.sure)
async def ok_add_tariff(message: Message, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        # берём данные из всех состояний
        tdata = await state.get_data()
        # добавляем новый заказ в БД
        await db.add_tariff(tdata['name'] ,tdata['description'], tdata['responses'], tdata['amount'])
        # устанавливаем нужное FSM состояние
        await state.set_state(st.AdminTariff.all_tariffs)
        # берём из БД статистику финансов пользователя
        tariffs = await db.all_tariffs()
        if not tariffs:
            await message.answer('Нет ни одного тарифа',
                                 reply_markup=kb.tariffs_menu)
        else:
            for tariff in tariffs:
                await message.answer(f'<b>Название:</b> {tariff.name}\n'
                                     f'<b>Описание:</b> {tariff.description}\n\n'
                                     f'<b>Откликов в день:</b> {tariff.responses}\n'
                                     f'<b>Стоимость:</b> {tariff.amount}₽',
                                     reply_markup=await kb.tariff_menu(tariff))
            await message.answer('Меню 👇',
                                 reply_markup=kb.tariffs_menu)
    except Exception:
        await message.answer('Произошла ошибка\n'
                             'Введите команду /start или свяжитесь с @mesudoteach')


"""-------------------------------------------Изменить тариф---------------------------------------------------"""
@admin.callback_query(F.data.startswith('admin-edit-tariff_'), st.AdminTariff.all_tariffs)
async def edit_tariff_name(callback: CallbackQuery, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        await callback.answer('')
        await state.update_data(tariff=callback.data.split('_')[1])
        # устанавливаем нужное FSM состояние
        await state.set_state(st.EditTariff.name)
        await callback.message.answer('Введите название для тарифа (до 25 символов)',
                             reply_markup=kb.cancel)
    except Exception:
        await callback.message.answer('Произошла ошибка\n'
                             'Введите команду /start или свяжитесь с @mesudoteach')


@admin.message(st.EditTariff.name)
async def edit_tariff_description(message: Message, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        if len(message.text) > 25:
            await message.answer('Название тарифа не должно быть более 25 символов',
                                 reply_markup=kb.cancel)
        else:
            # записываем в нужное нам состояние введённую информацию
            await state.update_data(name=message.text)
            # устанавливаем нужное FSM состояние
            await state.set_state(st.EditTariff.description)
            await message.answer('Введите описание тарифа',
                                 reply_markup=kb.cancel)
    except Exception:
        await message.answer('Произошла ошибка\n'
                             'Введите команду /start или свяжитесь с @mesudoteach')


@admin.message(st.EditTariff.description)
async def edit_tariff_responses(message: Message, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        if len(message.text) > 10000:
            await message.answer('Описание тарифа не должно быть более 1000 символов',
                                 reply_markup=kb.cancel)
        else:
            # записываем в нужное нам состояние введённую информацию
            await state.update_data(description=message.text)

            # устанавливаем нужное FSM состояние
            await state.set_state(st.EditTariff.responses)
            await message.answer('Введите количество доступных в день откликов по этому тарифу',
                                 reply_markup=kb.cancel)
    except Exception:
        await message.answer('Произошла ошибка\n'
                             'Введите команду /start или свяжитесь с @mesudoteach')


@admin.message(st.EditTariff.responses)
async def edit_tariff_amount(message: Message, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        if message.text.isdigit() and not message.text.isalpha():
            # записываем в нужное нам состояние введённую информацию
            await state.update_data(responses=int(message.text))
            # устанавливаем нужное FSM состояние
            await state.set_state(st.EditTariff.amount)
            await message.answer('Введите стоимость тарифа в рублях',
                                 reply_markup=kb.cancel)
        else:
            await message.answer('Введено некорректное значение\n'
                                 'Введите количество доступных в день откликов по этому тарифу',
                                 reply_markup=kb.cancel)
    except Exception:
        await message.answer('Произошла ошибка\n'
                             'Введите команду /start или свяжитесь с @mesudoteach')


@admin.message(st.EditTariff.amount)
async def sure_edit_tariff(message: Message, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        if message.text.isdigit() and not message.text.isalpha():
            # записываем в нужное нам состояние введённую информацию
            await state.update_data(amount=int(message.text))
            # устанавливаем нужное FSM состояние
            await state.set_state(st.EditTariff.sure)
            tdata = await state.get_data()
            await message.answer(f'Вы уверены, что хотите изменить данные тарифа на следующие?\n\n'
                                 f'<b>Название</b>: {tdata['name']}\n'
                                 f'<b>Описание</b>: {tdata['description']}\n\n'
                                 f'<b>Откликов в день</b>: {tdata['responses']}\n'
                                 f'<b>Стоимость</b>: {tdata['amount']}₽',
                                 reply_markup=kb.sure)
        else:
            await message.answer('Введено некорректное значение\n'
                                 'Введите стоимость тарифа в рублях',
                                 reply_markup=kb.cancel)
    except Exception:
        await message.answer('Произошла ошибка\n'
                             'Введите команду /start или свяжитесь с @mesudoteach')


@admin.message(F.text == '🌟 Да', st.EditTariff.sure)
async def ok_edit_tariff(message: Message, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        # берём данные из всех состояний
        tdata = await state.get_data()
        # добавляем новый заказ в БД
        await db.edit_tariff(tdata['tariff'] ,tdata['name'] ,tdata['description'], tdata['responses'], tdata['amount'])
        # устанавливаем нужное FSM состояние
        await state.set_state(st.AdminTariff.all_tariffs)
        # берём из БД статистику финансов пользователя
        tariffs = await db.all_tariffs()
        for tariff in tariffs:
            await message.answer(f'<b>Название:</b> {tariff.name}\n'
                                 f'<b>Описание:</b> {tariff.description}\n\n'
                                 f'<b>Откликов в день:</b> {tariff.responses}\n'
                                 f'<b>Стоимость:</b> {tariff.amount}₽',
                                 reply_markup=await kb.tariff_menu(tariff))
        await message.answer('Меню 👇',
                             reply_markup=kb.tariffs_menu)
    except Exception:
        await message.answer('Произошла ошибка\n'
                             'Введите команду /start или свяжитесь с @mesudoteach')


"""-------------------------------------------Удалить тариф---------------------------------------------------"""
@admin.callback_query(F.data.startswith('admin-delete-tariff_'), st.AdminTariff.all_tariffs)
async def sure_delete_tariff(callback: CallbackQuery, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        await callback.answer('')
        # устанавливаем нужное FSM состояние
        await state.set_state(st.AdminTariff.delete_tariff)
        await callback.message.edit_text('‼️ Вы действительно хотите удалить тариф?',
                             reply_markup=await kb.sure_delete_tariff(callback.data.split('_')[1]))
    except Exception:
        await callback.message.answer('Произошла ошибка\n'
                             'Введите команду /start или свяжитесь с @mesudoteach')


@admin.callback_query(F.data.startswith('cancel-delete-tariff_'), st.AdminTariff.delete_tariff)
async def cancel_delete_tariff(callback: CallbackQuery, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        # ответ на callback
        await callback.answer('')
        # устанавливаем нужное FSM состояние
        await state.set_state(st.AdminTariff.all_tariffs)
        tariff = await db.get_tariff(callback.data.split('_')[1])
        await callback.message.edit_text(f'<b>Название:</b> {tariff.name}\n'
                             f'<b>Описание:</b> {tariff.description}\n\n'
                             f'<b>Откликов в день:</b> {tariff.responses}\n'
                             f'<b>Стоимость:</b> {tariff.amount}₽',
                             reply_markup=await kb.tariff_menu(tariff))
    except Exception:
        await callback.message.answer('Произошла ошибка\n'
                                      'Введите команду /start или свяжитесь с @mesudoteach')


@admin.callback_query(F.data.startswith('ok-delete-tariff_'), st.AdminTariff.delete_tariff)
async def ok_delete_tariff(callback: CallbackQuery, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        # ответ на callback
        await callback.answer('')
        # устанавливаем нужное FSM состояние
        await state.set_state(st.AdminTariff.all_tariffs)
        await db.delete_tariff(callback.data.split('_')[1])
        await callback.message.delete()
    except Exception:
        await callback.message.answer('Произошла ошибка\n'
                                      'Введите команду /start или свяжитесь с @mesudoteach')


"""

Действия в разделе "Сделать рассылку"
----------------------------------------------------------------------------------------------
"""
@admin.message(AdminProtect(), F.text == '✍️ Сделать рассылку', st.AdminMenu.menu)
async def sendall_select_method(message: Message, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        # устанавливаем нужное FSM состояние
        await state.set_state(st.SendAll.select_method)
        # берём из БД статистику финансов пользователя
        await message.answer('Выберите метод рассылки:',
                         reply_markup=await kb.sendall_methods())
        await message.answer('Меню 👇',
                             reply_markup=kb.cancel)
    except Exception:
        await message.answer('Произошла ошибка\n'
                             'Введите команду /start или свяжитесь с @mesudoteach')


@admin.callback_query(F.data.startswith('sendall_'), st.SendAll.select_method)
async def sendall_message(callback: CallbackQuery, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        # ответ на callback
        await callback.answer('')
        # устанавливаем нужное FSM состояние
        await state.set_state(st.SendAll.message)
        await state.update_data(method=callback.data.split('_')[1])
        await callback.message.answer('Введите текст сообщения')
    except Exception:
        await callback.message.answer('Произошла ошибка\n'
                                      'Введите команду /start или свяжитесь с @mesudoteach')


@admin.message(st.SendAll.message)
async def sure_sendall(message: Message, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        # записываем в нужное нам состояние введённую информацию
        await state.update_data(message=message.text)
        # устанавливаем нужное FSM состояние
        await state.set_state(st.SendAll.sure)
        tdata = await state.get_data()
        recipients = 'Все' if tdata['method']=='1' else 'Заказчики' if tdata['method']=='2' else 'Разработчики'
        await message.answer(f'Вы уверены, что хотите сделать следующую рассылку?\n\n'
                             f'<b>Кто получит сообщение</b>: {recipients}\n'
                             f'<b>Сообщение</b>: {tdata['message']}',
                             reply_markup=kb.sure)
    except Exception:
        await message.answer('Произошла ошибка\n'
                             'Введите команду /start или свяжитесь с @mesudoteach')


@admin.message(AdminProtect(), F.text == '🌟 Да', st.SendAll.sure)
async def ok_sendall_sure(message: Message, bot: Bot, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        # берём данные из всех состояний
        tdata = await state.get_data()
        text = tdata['message']  # текст рассылки
        # берём tg_id всех пользователей бота
        recipients = await db.all_users() if tdata['method'] == '1' else await db.all_clients() if tdata['method'] == '2' else await db.all_developers()
        for recipient in recipients:
            # отправляем каждому пользователю сообщение
            await bot.send_message(chat_id=recipient.tg_id, text=text)
        # отправляем администратору сообщение, reply_markup — параметр с нужной клавиатурой
        await state.clear()
        await state.set_state(st.AdminMenu.menu)
        # отправляем администратору сообщение, reply_markup — параметр с нужной клавиатурой
        await message.answer('Рассылка успешно завершена', reply_markup=kb.admin_panel)
    except Exception:
        await message.answer('Произошла ошибка\n'
                             'Введите команду /start или свяжитесь с @mesudoteach')