from tkinter.ttk import Label

from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, LabeledPrice, PreCheckoutQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from pyexpat.errors import messages

from config import ADMIN_DEVELOPER_CHAT_ID
import app.database.requests as db
import app.states as st
import app.keyboards as kb

developer = Router()

@developer.callback_query(F.data == 'developer', st.Register.role)
async def developer_moderation(callback: CallbackQuery, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        if await db.is_moderation_developer(callback.from_user.id):
            await callback.answer('')
            await callback.message.answer('Ваша заявка на рассмотрении')
        else:
            # устанавливаем нужное FSM состояние
            await state.set_state(st.Register.moderation)
            await callback.answer('')
            await callback.message.answer('‼️ ВНИМАНИЕ ‼️\n\n'
                                          'Для того, чтобы стать разработчиком на нашей платформе, <b>ВАМ необходимо:</b>\n\n'
                                          '<b>1.</b> Убедиться, что Ваш аккаунт в телеграмме имеет "Имя пользователя"\n\n'
                                          '<b>2.</b> В ответ на это сообщение отправить ссылку на <b>Ваш гитхаб (обязательно</b>)\n\n'
                                          '<b>3.</b> Ожидать результата модерации', reply_markup=kb.back)
    except Exception:
        await callback.message.answer('Произошла ошибка\n'
                             'Введите команду /start или свяжитесь с @mesudoteach')


@developer.message(F.text == '🧑‍💻 Стать разработчиком', st.ClientMenu.menu)
async def become_developer(message: Message, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        if await db.is_developer(message.from_user.id):
            await state.clear()
            # устанавливаем нужное FSM состояние
            await state.set_state(st.DeveloperMenu.menu)
            await message.answer('Главное меню', reply_markup=kb.developer_main)
        elif await db.is_moderation_developer(message.from_user.id):
            await message.answer('Ваша заявка на рассмотрении')
        else:
            await db.add_client(message.from_user.id)
            # устанавливаем нужное FSM состояние
            await state.set_state(st.Register.moderation)
            await message.answer('‼️ ВНИМАНИЕ ‼️\n\n'
                                 'Для того, чтобы стать разработчиком на нашей платформе, <b>ВАМ необходимо:</b>\n\n'
                                 '<b>1.</b> Убедиться, что Ваш аккаунт в телеграмме имеет "Имя пользователя"\n\n'
                                 '<b>2.</b> В ответ на это сообщение отправить ссылку на <b>Ваш гитхаб (обязательно</b>)\n\n'
                                 '<b>3.</b> Ожидать результата модерации', reply_markup=kb.back)
    except Exception:
        await message.answer('Произошла ошибка\n'
                             'Введите команду /start или свяжитесь с @mesudoteach')


@developer.message(st.Register.moderation)
async def developer_moderation_github(message: Message, bot: Bot, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        # добавляем разработчика в БД
        await db.add_developer(message.from_user.id, message.from_user.username)
        await bot.send_message(chat_id=ADMIN_DEVELOPER_CHAT_ID,
                               text=f'‼️ ВНИМАНИЕ ‼️\n'
                                    f'<b>Новый разработчик:</b>\n\n'
                                    f'<b>Никнейм:</b> {message.from_user.username}\n'
                                    f'<b>GitHub:</b> {message.text}',
                               reply_markup=await kb.developer_moderation(message.from_user.id))
        # устанавливаем нужное FSM состояние
        await state.clear()
        await message.answer('‼️ Ваша заявка отправлена на модерацию')
    except Exception:
        await message.answer('Произошла ошибка\n'
                             'Введите команду /start или свяжитесь с @mesudoteach')


@developer.message(F.text == '◀️ Назад', st.Market.list)
@developer.message(F.text == '◀️ Назад', st.DeveloperProfile.profile)
async def developer_main_menu(message: Message, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        await state.clear()
        # устанавливаем нужное FSM состояние
        await state.set_state(st.DeveloperMenu.menu)
        await message.answer('Главное меню', reply_markup=kb.developer_main)
    except Exception:
        await message.answer('Произошла ошибка\n'
                             'Введите команду /start или свяжитесь с @mesudoteach')


"""

Действия в разделе "Биржа"
----------------------------------------------------------------------------------------------
"""
@developer.message(F.text == '❌ Отмена', st.Market.make_response)
@developer.message(F.text == '◀️ Назад', st.Market.order_info)
@developer.message(F.text == '💰 Биржа', st.DeveloperMenu.menu)
async def market_list(message: Message, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        # устанавливаем нужное FSM состояние
        await state.set_state(st.Market.list)
        await message.answer('💲 Заказы 💲')
        orders = await db.all_orders()
        for order in orders:
            await message.answer(f'<b>Название:</b> {order.title}\n',
                                 reply_markup=await kb.order_info(order.id))
        await message.answer('Меню 👇',
                             reply_markup=kb.back)
    except Exception:
        await message.answer('Произошла ошибка\n'
                             'Введите команду /start или свяжитесь с @mesudoteach')


@developer.callback_query(F.data.startswith('order-info_'), st.Market.list)
async def market_order_info(callback: CallbackQuery, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        # устанавливаем нужное FSM состояние
        await state.set_state(st.Market.order_info)
        await state.update_data(order_info=callback.data.split('_')[1])
        await callback.answer('')
        order = await db.get_order(callback.data.split('_')[1])
        is_response = await db.is_response_from_developer(callback.from_user.id)
        await callback.message.answer(f'Подробности заказа\n\n'
                                      f'<b>Название:</b> {order.title}\n'
                                      f'<b>Описание:</b> {order.description}'
                                      f'{f'\n\n‼️ <b>Вы уже откликнулись на этот заказ</b>' if is_response else ''}',
                                          reply_markup=None if is_response else await kb.make_response(order.id))
    except Exception:
        await callback.message.answer('Произошла ошибка\n'
                             'Введите команду /start или свяжитесь с @mesudoteach')


@developer.callback_query(F.data.startswith('make-response_'), st.Market.order_info)
async def market_make_response(callback: CallbackQuery, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        # устанавливаем нужное FSM состояние
        await state.set_state(st.Market.make_response)
        await callback.answer('')
        await callback.message.answer('Введите текст для отклика (не более 1000 символов)',
                                      reply_markup=kb.cancel)
    except Exception:
        await callback.message.answer('Произошла ошибка\n'
                             'Введите команду /start или свяжитесь с @mesudoteach')


@developer.message(st.Market.make_response)
async def market_send_response(message: Message, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        if len(message.text) > 10000:
            await message.answer('Текст отклика не должен быть более 1000 символов')
        else:
            # берём данные из всех состояний
            tdata = await state.get_data()
            await db.add_response(message.from_user.id, tdata['order_info'], message.text)
            await message.answer('Ваш отклик отправлен заказчику.')
            # устанавливаем нужное FSM состояние
            await state.set_state(st.Market.list)
            await message.answer('💲 Заказы 💲')
            orders = await db.all_orders()
            for order in orders:
                await message.answer(f'<b>Название:</b> {order.title}\n',
                                     reply_markup=await kb.order_info(order.id))
            await message.answer('Меню 👇',
                                 reply_markup=kb.back)
    except Exception:
        await message.answer('Произошла ошибка\n'
                             'Введите команду /start или свяжитесь с @mesudoteach')



"""

Действия в разделе "Мой профиль"
----------------------------------------------------------------------------------------------
"""
@developer.message(F.text == '◀️ Назад', st.DeveloperProfile.tariffs)
@developer.message(F.text == '🧑‍💻 Мой профиль', st.DeveloperMenu.menu)
async def developer_profile(message: Message, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        # устанавливаем нужное FSM состояние
        await state.set_state(st.DeveloperProfile.profile)
        developer_info = await db.get_developer(message.from_user.id)
        tariff = await db.get_tariff(developer_info.tariff)
        await message.answer(f'<b>Юзернейм:</b> {developer_info.username}\n'
                             f'<b>Тариф:</b> {tariff.name if tariff.name else 'Не выбран'}\n'
                             f'<b>Рейтинг:</b> {developer_info.rating if developer_info.rating > 0 else 'Нет оценок'}\n'
                             f'<b>Количество выполненных заказов:</b> {developer_info.completed_orders}\n'
                             f'<b>Количество доступных откликов:</b> {developer_info.responses}\n',
                                 reply_markup= kb.developer_profile)
    except Exception:
        await message.answer('Произошла ошибка\n'
                             'Введите команду /start или свяжитесь с @mesudoteach')


"""-------------------------------------------Выбор и покупка тарифа---------------------------------------------------"""
@developer.message(F.text == '🤖 Выбрать тариф', st.DeveloperProfile.profile)
async def list_of_tariffs(message: Message, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        # устанавливаем нужное FSM состояние
        await state.set_state(st.DeveloperProfile.tariffs)
        tariffs = await db.all_tariffs()
        for tariff in tariffs:
            await message.answer(f'<b>Название:</b> {tariff.name}\n'
                                 f'<b>Описание:</b> {tariff.description}\n',
                                 reply_markup=await kb.select_tariff(tariff))
        await message.answer('Меню 👇',
                             reply_markup=kb.back)
    except Exception:
        await message.answer('Произошла ошибка\n'
                             'Введите команду /start или свяжитесь с @mesudoteach')


@developer.callback_query(F.data.startswith('tariff_'), st.DeveloperProfile.tariffs)
async def select_tariff(callback: CallbackQuery, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        # устанавливаем нужное FSM состояние
        await state.set_state(st.DeveloperProfile.pay_tariff)
        await callback.answer('')
        tariff = await db.get_tariff(callback.data.split('_')[1])
        await callback.message.answer_invoice(title='Оплата тарифа',
                                              description='Оплата тарифа',
                                              payload=f'tariff_{tariff.id}',
                                              currency='XTR',
                                              prices=[LabeledPrice(label='XTR', amount=tariff.amount)])
    except Exception:
        await callback.message.answer('Произошла ошибка\n'
                             'Введите команду /start или свяжитесь с @mesudoteach')


@developer.pre_checkout_query()
async def pre_checkout_query(query: PreCheckoutQuery):
    await query.answer(True)


@developer.message(F.successful_payment.invoice_payload.startswith('tariff_'))
async def successful_payment(message: Message, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        #await message.bot.refund_star_payment(message.from_user.id,
                                              #message.successful_payment.telegram_payment_charge_id)
        tariff = await db.get_tariff(message.successful_payment.invoice_payload.split('_')[1])
        await db.tariff_payed(message.from_user.id, tariff)
        # устанавливаем нужное FSM состояние
        await state.set_state(st.DeveloperProfile.profile)
        developer_info = await db.get_developer(message.from_user.id)
        await message.answer(f'<b>Юзернейм:</b> {developer_info.username}\n'
                             f'<b>Тариф:</b> {tariff.name if tariff.name else 'Не выбран'}\n'
                             f'<b>Рейтинг:</b> {developer_info.rating if developer_info.rating > 0 else 'Нет оценок'}\n'
                             f'<b>Количество выполненных заказов:</b> {developer_info.completed_orders}\n'
                             f'<b>Количество доступных откликов:</b> {developer_info.responses}\n',
                             reply_markup=kb.developer_profile)
    except Exception:
        await message.answer('Произошла ошибка\n'
                             'Введите команду /start или свяжитесь с @mesudoteach')





"""

Чтение сообщений из закрытого чата (модерация)
----------------------------------------------------------------------------------------------

"""


@developer.callback_query(lambda callback: callback.message.chat.id == ADMIN_DEVELOPER_CHAT_ID, F.data.startswith('moderation-passed_'))  # хэндлер срабатывает только тогда, когда в нужный чат присылается сообщение
async def moderation_passed(callback: Message, bot: Bot):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        # ответ на callback
        await callback.answer('Спасибо за работу')
        await callback.message.delete()
        # извлекаем из callback id запроса
        developer_info = await db.developer_activate(callback.data.split('_')[1])
        await bot.send_message(chat_id=developer_info.tg_id, text='<b>‼️ Вам одобрен доступ к панели разработчика</b>\n\n'
                                                                  'Чтобы её открыть, отправьте команду /start')
    except Exception:
        await callback.message.answer('Произошла ошибка\n'
                             'Введите команду /start или свяжитесь с @mesudoteach')


@developer.callback_query(lambda callback: callback.message.chat.id == ADMIN_DEVELOPER_CHAT_ID, F.data.startswith('moderation-failed_'))  # хэндлер срабатывает только тогда, когда в нужный чат присылается сообщение
async def moderation_failed(callback: Message, bot: Bot):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        # ответ на callback
        await callback.answer('Спасибо за работу')
        await callback.message.delete()
        # извлекаем из callback id запроса
        developer_info = await db.delete_developer(callback.data.split('_')[1])
        await bot.send_message(chat_id=developer_info.tg_id, text='<b>‼️ К сожалению, вам не одобрен доступ к панели разработчика</b>')
    except Exception:
        await callback.message.answer('Произошла ошибка\n'
                             'Введите команду /start или свяжитесь с @mesudoteach')