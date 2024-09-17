from tkinter.ttk import Label

from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, LabeledPrice, PreCheckoutQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from pyexpat.errors import messages
from sqlalchemy.util import await_only

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


@developer.message(F.text == '◀️ Назад', st.CompletedOrder.order_info)
@developer.message(F.text == '◀️ Назад', st.CompletedOrder.list)
@developer.message(F.text == '◀️ Назад', st.DeveloperResponse.delete_response)
@developer.message(F.text == '◀️ Назад', st.DeveloperResponse.list)
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
@developer.message(F.text == '💰 Биржа', st.DeveloperMenu.menu)
async def market_list(message: Message, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        if await db.is_available_response(message.from_user.id) > 0:
            await message.answer('💲 Заказы 💲')
            orders = await db.all_orders()
            total_pages = (len(orders) + 10 - 1) // 10  # Общее количество страниц
            # устанавливаем нужное FSM состояние
            await state.set_state(st.Market.total_pages)
            await state.update_data(total_pages=total_pages)
            # устанавливаем нужное FSM состояние
            await state.set_state(st.Market.list)
            orders = await db.all_orders_pagination(1)
            await message.answer(f'<b>Страница 1 из {total_pages}</b>',
                                     reply_markup=await kb.all_orders_pagination(orders, 1, total_pages))
            await message.answer('Меню 👇',
                                 reply_markup=kb.back)
        else:
            await message.answer('‼️ Истрачен ежедневный лимит откликов')
    except Exception:
        await message.answer('Произошла ошибка\n'
                             'Введите команду /start или свяжитесь с @mesudoteach')


@developer.callback_query(F.data.startswith('next-market-order_'), st.Market.list)
async def next_market_order(callback: CallbackQuery, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        await callback.answer('')
        page = int(callback.data.split('_')[1])
        orders = await db.all_orders_pagination(page)
        tdata = await state.get_data()
        total_pages = tdata['total_pages']
        await callback.message.edit_text(f'<b>Страница {page} из {total_pages}</b>',
                             reply_markup=await kb.all_orders_pagination(orders, page, total_pages))
    except Exception:
        await callback.message.answer('Произошла ошибка\n'
                             'Введите команду /start или свяжитесь с @mesudoteach')


@developer.callback_query(F.data.startswith('prev-market-order_'), st.Market.list)
async def prev_market_order(callback: CallbackQuery, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        await callback.answer('')
        page = int(callback.data.split('_')[1])
        orders = await db.all_orders_pagination(page)
        tdata = await state.get_data()
        total_pages = tdata['total_pages']
        await callback.message.edit_text(f'<b>Страница {page} из {total_pages}</b>',
                             reply_markup=await kb.all_orders_pagination(orders, page, total_pages))
    except Exception:
        await callback.message.answer('Произошла ошибка\n'
                             'Введите команду /start или свяжитесь с @mesudoteach')


@developer.callback_query(F.data.startswith('order-info_'), st.Market.list)
async def market_order_info(callback: CallbackQuery, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        await callback.answer('')
        # устанавливаем нужное FSM состояние
        await state.set_state(st.Market.order_info)
        order = await db.get_order(callback.data.split('_')[1])
        if await db.developer_is_client(callback.from_user.id, order):
            await callback.message.answer(f'Подробности заказа\n\n'
                                          f'<b>Название:</b> {order.title}\n'
                                          f'<b>Описание:</b> {order.description}\n'
                                          f'‼️ <b>Вы не можете откликнуться на свой заказ</b>',
                                          reply_markup=await kb.market_order_info())
        else:
            is_response = await db.is_response_from_developer_to_order(callback.from_user.id,
                                                                       callback.data.split('_')[1])
            await callback.message.answer(f'Подробности заказа\n\n'
                                          f'<b>Название:</b> {order.title}\n'
                                          f'<b>Описание:</b> {order.description}'
                                          f'{f'\n\n‼️ <b>Вы уже откликнулись на этот заказ</b>' if is_response else ''}',
                                              reply_markup=await kb.market_order_info()
                                              if is_response else await kb.make_response(order.id))
    except Exception:
        await callback.message.answer('Произошла ошибка\n'
                             'Введите команду /start или свяжитесь с @mesudoteach')


@developer.callback_query(F.data == 'hide_market_order_info', st.Market.order_info)
async def hide_market_order_info(callback: CallbackQuery, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        await state.set_state(st.Market.list)
        await callback.answer('')
        await callback.message.delete()
    except Exception:
        await callback.message.answer('Произошла ошибка\n'
                             'Введите команду /start или свяжитесь с @mesudoteach')


@developer.callback_query(F.data.startswith('make-response_'), st.Market.order_info)
async def market_make_response(callback: CallbackQuery, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        await state.update_data(order_info=callback.data.split('_')[1])
        await state.set_state(st.Market.make_response)
        await callback.answer('')
        order = await db.get_order(callback.data.split('_')[1])
        await callback.message.answer(f'<b>Заказ:</b> {order.title}\n'
                                      f'Введите текст для отклика (не более 1000 символов)',
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
            if await db.is_available_response(message.from_user.id) > 0:
                await message.answer('💲 Заказы 💲')
                orders = await db.all_orders()
                total_pages = (len(orders) + 10 - 1) // 10  # Общее количество страниц
                # устанавливаем нужное FSM состояние
                await state.set_state(st.Market.total_pages)
                await state.update_data(total_pages=total_pages)
                # устанавливаем нужное FSM состояние
                await state.set_state(st.Market.list)
                orders = await db.all_orders_pagination(1)
                await message.answer(f'<b>Страница 1 из {total_pages}</b>',
                                     reply_markup=await kb.all_orders_pagination(orders, 1, total_pages))
                await message.answer('Меню 👇',
                                     reply_markup=kb.back)
            else:
                await state.clear()
                # устанавливаем нужное FSM состояние
                await state.set_state(st.DeveloperMenu.menu)
                await message.answer('‼️ Истрачен ежедневный лимит откликов')
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

Действия в разделе "Мои отклики"
----------------------------------------------------------------------------------------------
"""
@developer.message(F.text == '💥️ Мои отклики', st.DeveloperMenu.menu)
async def developer_responses(message: Message, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        # устанавливаем нужное FSM состояние
        await state.set_state(st.DeveloperResponse.list)
        if await db.is_response_from_developer(message.from_user.id):
            responses = await db.developer_responses(message.from_user.id)
            for response in responses:
                order = await db.get_order(response.order)
                await message.answer(f'{f'<b>Заказ</b>: {order.title}' if order else 'Заказ выполнен другим исполнителем'}\n'
                                     f'<b>Отклик</b>: {response.description}\n'
                                     f'<b>Статус</b>: {response.status}',
                                     reply_markup=await kb.delete_response(response.id))
            await message.answer('Меню 👇',
                                 reply_markup=kb.back)
        else:
            await message.answer('У вас нет откликов',
                                     reply_markup= kb.back)
    except Exception:
        await message.answer('Произошла ошибка\n'
                             'Введите команду /start или свяжитесь с @mesudoteach')


@developer.callback_query(F.data.startswith('delete-response_'), st.DeveloperResponse.list)
async def delete_response(callback: CallbackQuery, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        # ответ на callback
        await callback.answer('')
        # устанавливаем нужное FSM состояние
        await state.set_state(st.DeveloperResponse.delete_response)
        await callback.message.edit_text(f'‼️ Вы действительно хотите удалить отклик?',
                                      reply_markup=await kb.sure_delete_response(callback.data.split('_')[1]))
    except Exception:
        await callback.message.answer('Произошла ошибка\n'
                                      'Введите команду /start или свяжитесь с @mesudoteach')


@developer.callback_query(F.data.startswith('cancel-delete-response_'), st.DeveloperResponse.delete_response)
async def cancel_delete_response(callback: CallbackQuery, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        # ответ на callback
        await callback.answer('')
        # устанавливаем нужное FSM состояние
        await state.set_state(st.DeveloperResponse.list)
        response = await db.get_response(callback.data.split('_')[1])
        order = await db.get_order(response.order)
        await callback.message.edit_text(f'<b>Заказ</b>: {order.title}\n'
                                 f'<b>Отклик</b>: {response.description}\n'
                                 f'<b>Статус</b>: {response.status}',
                                 reply_markup=await kb.delete_response(response.id))
    except Exception:
        await callback.message.answer('Произошла ошибка\n'
                                      'Введите команду /start или свяжитесь с @mesudoteach')


@developer.callback_query(F.data.startswith('ok-delete-response_'), st.DeveloperResponse.delete_response)
async def ok_delete_response(callback: CallbackQuery, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        # ответ на callback
        await callback.answer('')
        # устанавливаем нужное FSM состояние
        await state.set_state(st.DeveloperResponse.list)
        await db.delete_response(callback.data.split('_')[1])
        await callback.message.delete()
    except Exception:
        await callback.message.answer('Произошла ошибка\n'
                                      'Введите команду /start или свяжитесь с @mesudoteach')


"""

Действия в разделе "Выполненные заказы"
----------------------------------------------------------------------------------------------
"""
@developer.message(F.text == '◀️ Назад', st.CompletedOrder.order_info)
@developer.message(F.text == '🔹 Выполненные заказы', st.DeveloperMenu.menu)
async def completed_orders(message: Message, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        orders = await db.completed_orders(message.from_user.id)
        if not orders:
            # устанавливаем нужное FSM состояние
            await state.set_state(st.CompletedOrder.list)
            await message.answer('Нет заказов',
                                 reply_markup=kb.back)
        else:
            total_pages = (len(orders) + 5 - 1) // 5  # Общее количество страниц
            await state.update_data(total_pages=total_pages)
            await state.update_data(page=1)
            # устанавливаем нужное FSM состояние
            await state.set_state(st.CompletedOrder.list)
            orders = await db.order_history_pagination(message.from_user.id, 1)
            await message.answer(f'<b>Страница 1 из {total_pages}</b>',
                                 reply_markup=await kb.completed_orders_pagination(orders, 1, total_pages))
            await message.answer('Меню 👇',
                             reply_markup=kb.back)
    except Exception:
        await message.answer('Произошла ошибка\n'
                                      'Введите команду /start или свяжитесь с @mesudoteach')


@developer.callback_query(F.data.startswith('next-completed-order_'), st.CompletedOrder.list)
async def next_completed_order(callback: CallbackQuery, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        await callback.answer('')
        page = int(callback.data.split('_')[1])
        await state.update_data(page=page)
        orders = await db.completed_orders_pagination(callback.from_user.id, page)
        tdata = await state.get_data()
        total_pages = tdata['total_pages']
        await callback.message.edit_text(f'<b>Страница {page} из {total_pages}</b>',
                             reply_markup=await kb.completed_orders_pagination(orders, page, total_pages))
    except Exception:
        await callback.message.answer('Произошла ошибка\n'
                             'Введите команду /start или свяжитесь с @mesudoteach')


@developer.callback_query(F.data.startswith('prev-completed-order_'), st.CompletedOrder.list)
async def prev_completed_order(callback: CallbackQuery, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        await callback.answer('')
        page = int(callback.data.split('_')[1])
        await state.update_data(page=page)
        orders = await db.completed_orders_pagination(callback.from_user.id ,page)
        tdata = await state.get_data()
        total_pages = tdata['total_pages']
        await callback.message.edit_text(f'<b>Страница {page} из {total_pages}</b>',
                             reply_markup=await kb.completed_orders_pagination(orders, page, total_pages))
    except Exception:
        await callback.message.answer('Произошла ошибка\n'
                             'Введите команду /start или свяжитесь с @mesudoteach')


@developer.callback_query(F.data.startswith('completed-order-info_'), st.CompletedOrder.list)
async def completed_order_info(callback: CallbackQuery, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        # ответ на callback
        await callback.answer('')
        # устанавливаем нужное FSM состояние
        await state.set_state(st.CompletedOrder.order_info)
        order = await db.get_completed_order(callback.data.split('_')[1])
        await callback.message.edit_text(f'<b>Заказ:</b> {order.title}\n'
                                         f'<b>Описание заказа:</b> {order.description}\n'
                                         f'<b>Оценка заказчика:</b>  {order.mark_for_developer 
                                         if order.mark_for_developer else 'Не оценено'}\n'
                                         f'<b>Комментарий заказчика:</b> {order.feedback_about_developer 
                                         if order.feedback_about_developer else 'Нет комментария'}\n'
                                         f'<b>Дата:</b> {order.date.strftime('%d.%m.%Y')}\n',
                                     reply_markup=await kb.completed_order_info())
    except Exception:
        await callback.message.answer('Произошла ошибка\n'
                                      'Введите команду /start или свяжитесь с @mesudoteach')


@developer.callback_query(F.data == 'hide_completed_order_info', st.CompletedOrder.order_info)
async def hide_completed_order_info(callback: CallbackQuery, state: FSMContext):
    # конструкция try except ловит и выводит сообщение об ошибке,
    # а также не даёт им остановить работу программы
    try:
        # ответ на callback
        await callback.answer('')
        # устанавливаем нужное FSM состояние
        await state.set_state(st.CompletedOrder.list)
        tdata = await state.get_data()
        page = tdata['page']
        total_pages = tdata['total_pages']
        orders = await db.order_history_pagination(callback.from_user.id, page)
        await callback.message.edit_text(f'<b>Страница {page} из {total_pages}</b>',
                             reply_markup=await kb.completed_orders_pagination(orders, page, total_pages))
    except Exception:
        await callback.message.answer('Произошла ошибка\n'
                                      'Введите команду /start или свяжитесь с @mesudoteach')


"""

Чтение сообщений из закрытого чата (модерация)
----------------------------------------------------------------------------------------------

"""


@developer.callback_query(lambda callback: callback.message.chat.id == ADMIN_DEVELOPER_CHAT_ID, F.data.startswith('moderation-passed_'))  # хэндлер срабатывает только тогда, когда в нужный чат присылается сообщение
async def moderation_passed(callback: CallbackQuery, bot: Bot):
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
async def moderation_failed(callback: CallbackQuery, bot: Bot):
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