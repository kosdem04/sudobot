import datetime

from app.database.models import async_session
from app.database.models import *
from sqlalchemy import select, update, delete, desc, not_
from sqlalchemy.orm import joinedload



"""

Запросы клиентов к БД
----------------------------------------------------------------------------------------------
"""
# проверка, существует ли клиент с данным tg_id в БД
async def is_client(tg_id):
    async with async_session() as session:
        return True if await session.scalar(select(Client).where(Client.tg_id == tg_id)) else False


# добавляем нового клиента в БД
async def add_client(tg_id):
    async with async_session() as session:
        session.add(Client(tg_id=tg_id))
        await session.commit()


# берём из БД данные конкретного клиента
async def get_client(tg_id):
    async with async_session() as session:
        return await session.scalar(select(Client).where(Client.tg_id == tg_id))


# берём из БД все заказы конкретного клиента
async def client_orders(tg_id):
    async with async_session() as session:
        orders = await session.execute(select(Order).where(Order.client == tg_id))
        # Получаем результаты запроса из statistics и вызываем scalars(),
        # чтобы получить скалярные значения (простые значения, а не кортежи).
        # Затем метод all() используется для извлечения всех результатов запроса.
        orders = orders.scalars().all()
        return orders


# берём из БД все заказы конкретного клиента
async def client_available_orders(tg_id):
    async with async_session() as session:
        orders = await session.execute(select(Order).where(Order.client == tg_id, Order.available == True))
        # Получаем результаты запроса из statistics и вызываем scalars(),
        # чтобы получить скалярные значения (простые значения, а не кортежи).
        # Затем метод all() используется для извлечения всех результатов запроса.
        orders = orders.scalars().all()
        return orders


# берём из БД все заказы конкретного клиента
async def client_orders_pagination(tg_id, page):
    async with async_session() as session:
        # Сортируем заказы по дате создания в порядке убывания, пропускаем первые 10 и ограничиваем результат до 5
        orders = await session.execute(
            select(Order).where(Order.client == tg_id)
            .order_by(Order.date.desc())  # Сортировка по дате создания
            .offset((page - 1) * 5)  # Пропускаем первые 5 заказов
            .limit(5)  # Ограничение до 10 заказов
        )
        orders = orders.scalars().all()
        return orders


# берём из БД все заказы конкретного клиента
async def client_available_orders_pagination(tg_id, page):
    async with async_session() as session:
        # Сортируем заказы по дате создания в порядке убывания, пропускаем первые 10 и ограничиваем результат до 5
        orders = await session.execute(
            select(Order).where(Order.client == tg_id, Order.available == True)
            .order_by(Order.date.desc())  # Сортировка по дате создания
            .offset((page - 1) * 5)  # Пропускаем первые 5 заказов
            .limit(5)  # Ограничение до 10 заказов
        )
        orders = orders.scalars().all()
        return orders


# добавляем заказ в БД
async def add_order(client, title, description):
    async with async_session() as session:
        order = Order(client=client, title=title, description=description, date=datetime.datetime.now())
        session.add(order)
        await session.commit()
        await session.refresh(order)
        return order


# после успешного прохождения модерации отмечаем заказ как доступный
async def available_order(order_id):
    async with async_session() as session:
        order = await session.scalar(select(Order).where(Order.id == order_id))
        order.available = True
        await session.commit()
        await session.refresh(order)
        return order


# удаляем определённый заказ из БД
async def delete_order(order_id):
    async with async_session() as session:
        order = await session.scalar(select(Order).where(Order.id == order_id))
        # обновляем данные
        await session.execute(update(Response).where(Response.order == order_id).values(
            status='Клиент удалил заказ'))
        await session.delete(order)
        await session.commit()
        return order


# берём данные конкретного заказа
async def get_order(order_id):
    async with async_session() as session:
        return await session.scalar(select(Order).options(joinedload(Order.client_rel)).where(Order.id == order_id))

# изменение данных о заказе
async def edit_order(order_id, title, description):
    async with async_session() as session:
        await session.execute(update(Order).where(Order.id == order_id).values(title=title, description=description))
        await session.commit()


# считаем общее количество откликов для определённого заказа
async def total_response(order_id):
    async with async_session() as session:
        total = await session.execute(select(Response).where(Response.order == order_id,
                                                             Response.status == 'На рассмотрении у заказчика'))
        # Получаем результаты запроса из statistics и вызываем scalars(),
        # чтобы получить скалярные значения (простые значения, а не кортежи).
        # Затем метод all() используется для извлечения всех результатов запроса.
        total = total.scalars().all()
        return len(total)


# берём из БД все отклики по текущему заказу
async def client_responses(order_id):
    async with async_session() as session:
        responses = await session.execute(select(Response).where(Response.order == order_id,
                                                                 Response.status == 'На рассмотрении у заказчика'))
        # Получаем результаты запроса из statistics и вызываем scalars(),
        # чтобы получить скалярные значения (простые значения, а не кортежи).
        # Затем метод all() используется для извлечения всех результатов запроса.
        responses = responses.scalars().all()
        return responses


# берём из БД все заказы конкретного клиента
async def client_responses_pagination(order_id, page):
    async with async_session() as session:
        # Сортируем заказы по дате создания в порядке убывания, пропускаем первые 10 и ограничиваем результат до 5
        responses = await session.execute(
            select(Response).where(Response.order == order_id,
                                   Response.status == 'На рассмотрении у заказчика')
            .order_by(Response.id.desc())  # Сортировка по id
            .offset((page - 1) * 5)  # Пропускаем первые 5 заказов
            .limit(5)  # Ограничение до 5 заказов
        )
        responses = responses.scalars().all()
        return responses


# после успешной модерации разрешаем разработчику доступ к панели разработчика
async def refuse_response(response_id):
    async with async_session() as session:
        await session.execute(update(Response).where(Response.id == response_id).values(status='Отказано'))
        await session.commit()


# берём данные о конкретном отклике
async def get_response(response_id):
    async with async_session() as session:
        return await session.scalar(select(Response).options(joinedload(Response.developer_rel), joinedload(Response.order_rel))
                                    .where(Response.id == response_id))


# берём из БД все отзывы о разработчике
async def last_feedbacks_about_developer(tg_id):
    async with async_session() as session:
        feedback = await session.execute(select(CompletedOrder).where(CompletedOrder.developer == tg_id,
                                                                      CompletedOrder.mark_for_developer)
                                         .order_by(CompletedOrder.date.desc())
                                         .limit(3)  # Ограничение до 10 заказов
                                         )
        # Получаем результаты запроса из statistics и вызываем scalars(),
        # чтобы получить скалярные значения (простые значения, а не кортежи).
        # Затем метод all() используется для извлечения всех результатов запроса.
        feedback = feedback.scalars().all()
        return feedback


# проверка, есть ли для заказа отклики
async def is_available_response_for_order(response_id):
    async with async_session() as session:
        response =  await session.scalar(select(Response).where(Response.id == response_id))
        return True if await session.scalar(select(Response).where(Response.order == response.order,
                                                                   Response.status == 'На рассмотрении у заказчика')) else False


# после успешной модерации разрешаем разработчику доступ к панели разработчика
async def order_complete(response_id):
    async with async_session() as session:
        response = await session.scalar(select(Response).where(Response.id == response_id))
        order = await session.scalar(select(Order).where(Order.id == response.order))
        developer = await session.scalar(select(Developer).where(Developer.tg_id == response.developer))
        client = await session.scalar(select(Client).where(Client.tg_id == order.client))
        session.add(CompletedOrder(client=order.client, developer=developer.tg_id, title=order.title,
                                   description=order.description, date=datetime.datetime.now()))
        developer.completed_orders = developer.completed_orders + 1
        client.completed_orders = client.completed_orders + 1
        # обновляем данные
        await session.execute(update(Response).where(Response.order == response.order).values(
            status='Заказ выполнен другим исполнителем'))
        # удаляем нужный отклик
        await session.delete(response)
        await session.delete(order)
        await session.commit()


# берём из БД всю историю заказов конкретного клиента
async def order_history(tg_id):
    async with async_session() as session:
        orders = await session.execute(select(CompletedOrder).where(CompletedOrder.client == tg_id))
        # Получаем результаты запроса из statistics и вызываем scalars(),
        # чтобы получить скалярные значения (простые значения, а не кортежи).
        # Затем метод all() используется для извлечения всех результатов запроса.
        orders = orders.scalars().all()
        return orders


# Отображение всех заказов
async def order_history_pagination(tg_id, page):
    async with async_session() as session:
        # Сортируем заказы по дате создания в порядке убывания, пропускаем первые 10 и ограничиваем результат до 5
        orders = await session.execute(
            select(CompletedOrder).where(CompletedOrder.client == tg_id)
            .order_by(CompletedOrder.date.desc())  # Сортировка по дате создания
            .offset((page-1) * 5)  # Пропускаем первые 10 заказов
            .limit(5)    # Ограничение до 10 заказов
        )
        orders = orders.scalars().all()
        return orders


# проверка, существует ли разработчик с данным tg_id в БД, который прошёл модерацию
async def is_feedback_about_developer(order_id):
    async with async_session() as session:
        return True if await session.scalar(select(CompletedOrder).where(CompletedOrder.id == order_id,
                                                                    CompletedOrder.mark_for_developer)) else False


# проверка, существует ли разработчик с данным tg_id в БД, который прошёл модерацию
async def is_feedback_about_client(order_id):
    async with async_session() as session:
        return True if await session.scalar(select(CompletedOrder).where(CompletedOrder.id == order_id,
                                                                    CompletedOrder.mark_for_client)) else False


# берём из БД все отзывы о разработчике
async def feedbacks_about_developer(tg_id):
    async with async_session() as session:
        feedback = await session.execute(select(CompletedOrder).where(CompletedOrder.developer == tg_id,
                                                                      CompletedOrder.mark_for_developer))
        # Получаем результаты запроса из statistics и вызываем scalars(),
        # чтобы получить скалярные значения (простые значения, а не кортежи).
        # Затем метод all() используется для извлечения всех результатов запроса.
        feedback = feedback.scalars().all()
        return feedback


# после успешной модерации разрешаем разработчику доступ к панели разработчика
async def add_client_feedback(order_id, mark, feedback, total_feedbacks, mark_sum_about_developer):
    async with async_session() as session:
        order = await session.scalar(select(CompletedOrder).where(CompletedOrder.id == order_id))
        developer = await session.scalar(select(Developer).where(Developer.tg_id == order.developer))
        developer.rating = (mark_sum_about_developer + int(mark))/(total_feedbacks+1)
        # обновляем данные
        await session.execute(update(CompletedOrder).where(CompletedOrder.id == order_id).values(
            mark_for_developer=int(mark), feedback_about_developer=feedback))
        await session.commit()


# после успешной модерации разрешаем разработчику доступ к панели разработчика
async def edit_client_feedback(order_id, mark, feedback, total_feedbacks, mark_sum_about_developer):
    async with async_session() as session:
        order = await session.scalar(select(CompletedOrder).where(CompletedOrder.id == order_id))
        developer = await session.scalar(select(Developer).where(Developer.tg_id == order.developer))
        developer.rating = ((mark_sum_about_developer - order.mark_for_developer) + int(mark))/total_feedbacks
        # обновляем данные
        await session.execute(update(CompletedOrder).where(CompletedOrder.id == order_id).values(
            mark_for_developer=int(mark), feedback_about_developer=feedback))
        await session.commit()


"""

Запросы разработчиков к БД
----------------------------------------------------------------------------------------------
"""
# проверка, существует ли разработчик с данным tg_id в БД, который прошёл модерацию
async def is_developer(tg_id):
    async with async_session() as session:
        return True if await session.scalar(select(Developer).where(Developer.tg_id == tg_id,
                                                                    Developer.moderation == True)) else False


# берём данные о конкретном разработчике из БД
async def get_developer(tg_id):
    async with async_session() as session:
        return await session.scalar(select(Developer).options(joinedload(Developer.tariff_rel)).where(Developer.tg_id == tg_id))


# проверка, существует ли разработчик с данным tg_id в БД, который находится на модерации
async def is_moderation_developer(tg_id):
    async with async_session() as session:
        return True if await session.scalar(select(Developer).where(Developer.tg_id == tg_id,
                                                                    Developer.moderation == False)) else False


# добавление нового разработчика в БД (на модерации)
async def add_developer(tg_id, username):
    async with async_session() as session:
        session.add(Developer(tg_id=tg_id, username=username))
        await session.commit()


# после успешной модерации разрешаем разработчику доступ к панели разработчика
async def developer_activate(developer_id):
    async with async_session() as session:
        developer = await session.scalar(select(Developer).where(Developer.tg_id == developer_id))
        developer.moderation = True
        await session.commit()
        await session.refresh(developer)
        return developer


# удаляем конкретного пользователя из БД
async def delete_developer(developer_id):
    async with async_session() as session:
        developer = await session.scalar(select(Developer).where(Developer.tg_id == developer_id))
        await session.delete(developer)
        await session.commit()
        return developer


# Отображение всех тарифов
async def all_tariffs():
    async with async_session() as session:
        tariffs = await session.execute(select(Tariff))
        # Получаем результаты запроса из statistics и вызываем scalars(),
        # чтобы получить скалярные значения (простые значения, а не кортежи).
        # Затем метод all() используется для извлечения всех результатов запроса.
        tariffs = tariffs.scalars().all()
        return tariffs


# Отображение всех заказов
async def get_tariff(tariff_id):
    async with async_session() as session:
        return await session.scalar(select(Tariff).where(Tariff.id == tariff_id))


# когда происходит оплата тарифа, обновляем данные пользователя
async def tariff_payed(developer_id, tariff):
    async with async_session() as session:
        await session.execute(update(Developer).where(Developer.tg_id == developer_id).values(
            responses=tariff.responses, tariff=tariff.id, subscription_end_date=datetime.datetime.now() + datetime.timedelta(days=30)))
        await session.commit()


# Отображение всех заказов
async def all_orders():
    async with async_session() as session:
        # Сортируем заказы по дате создания в порядке убывания и ограничиваем результат до 10
        orders = await session.execute(select(Order).where(Order.available == True)
            .order_by(Order.date.desc())  # Сортировка по дате создания
        )
        orders = orders.scalars().all()
        return orders


# Отображение всех заказов
async def all_orders_pagination(page):
    async with async_session() as session:
        # Сортируем заказы по дате создания в порядке убывания, пропускаем первые 10 и ограничиваем результат до 5
        orders = await session.execute(
            select(Order).where(Order.available == True)
            .order_by(Order.date.desc())  # Сортировка по дате создания
            .offset((page-1)*10)  # Пропускаем первые 10 заказов
            .limit(10)    # Ограничение до 10 заказов
        )
        orders = orders.scalars().all()
        return orders


# добавление нового отклика на заказ
async def add_response(developer_id, order_id, description):
    async with async_session() as session:
        session.add(Response(developer=developer_id, order=order_id, description=description,
                             status='На рассмотрении у заказчика'))
        developer =await session.scalar(select(Developer).where(Developer.tg_id == developer_id))
        developer.responses = developer.responses - 1
        await session.commit()


async def is_response_from_developer(developer_id):
    async with async_session() as session:
        return True if await session.scalar(select(Response).where(Response.developer == developer_id)) else False


async def is_response_from_developer_to_order(developer_id, order_id):
    async with async_session() as session:
        return True if await session.scalar(select(Response).where(Response.developer == developer_id,
                                                                   Response.order == order_id)) else False


# удаляем определённый отклик из БД
async def delete_response(response_id):
    async with async_session() as session:
        response = await session.scalar(select(Response).where(Response.id == response_id))
        await session.delete(response)
        await session.commit()


# берём из БД все отклики по текущему заказу
async def developer_responses(tg_id):
    async with async_session() as session:
        responses = await session.execute(select(Response).where(Response.developer == tg_id))
        # Получаем результаты запроса из statistics и вызываем scalars(),
        # чтобы получить скалярные значения (простые значения, а не кортежи).
        # Затем метод all() используется для извлечения всех результатов запроса.
        responses = responses.scalars().all()
        return responses


# Отображение всех заказов
async def developer_responses_pagination(tg_id, page):
    async with async_session() as session:
        # Сортируем заказы по дате создания в порядке убывания, пропускаем первые 10 и ограничиваем результат до 5
        responses = await session.execute(
            select(Response).where(Response.developer == tg_id)
            .order_by(Response.id.desc())  # Сортировка по дате создания
            .offset((page-1) * 5)  # Пропускаем первые 10 заказов
            .limit(5)    # Ограничение до 10 заказов
        )
        responses = responses.scalars().all()
        return responses


# проверка, остались ли у разработчика отклики
async def is_available_response(tg_id):
    async with async_session() as session:
        return await session.scalar(select(Developer.responses).where(Developer.tg_id == tg_id,
                                                                    Developer.moderation == True))


# проверка, есть ли для заказа отклики
async def developer_is_client(tg_id, order):
    async with async_session() as session:
        return True if await session.scalar(select(Order).where(Order.id == order.id,
            Order.client == tg_id)) else False


# берём из БД всю историю заказов конкретного клиента
async def completed_orders(tg_id):
    async with async_session() as session:
        orders = await session.execute(select(CompletedOrder).where(CompletedOrder.developer == tg_id))
        # Получаем результаты запроса из statistics и вызываем scalars(),
        # чтобы получить скалярные значения (простые значения, а не кортежи).
        # Затем метод all() используется для извлечения всех результатов запроса.
        orders = orders.scalars().all()
        return orders


# Отображение всех заказов
async def completed_orders_pagination(tg_id, page):
    async with async_session() as session:
        # Сортируем заказы по дате создания в порядке убывания, пропускаем первые 10 и ограничиваем результат до 5
        orders = await session.execute(
            select(CompletedOrder).where(CompletedOrder.developer == tg_id)
            .order_by(CompletedOrder.date.desc())  # Сортировка по дате создания
            .offset((page-1) * 5)  # Пропускаем первые 10 заказов
            .limit(5)    # Ограничение до 10 заказов
        )
        orders = orders.scalars().all()
        return orders


# получение информации о конкретном выполненном заказе
async def get_completed_order(order_id):
    async with async_session() as session:
        return await session.scalar(select(CompletedOrder).options(joinedload(CompletedOrder.developer_rel)).
                                    where(CompletedOrder.id == order_id))


# берём из БД все отзывы о разработчике
async def feedbacks_about_client(tg_id):
    async with async_session() as session:
        feedback = await session.execute(select(CompletedOrder).where(CompletedOrder.client == tg_id,
                                                                      CompletedOrder.mark_for_client))
        # Получаем результаты запроса из statistics и вызываем scalars(),
        # чтобы получить скалярные значения (простые значения, а не кортежи).
        # Затем метод all() используется для извлечения всех результатов запроса.
        feedback = feedback.scalars().all()
        return feedback


# берём из БД все отзывы о разработчике
async def last_feedbacks_about_client(tg_id):
    async with async_session() as session:
        feedback = await session.execute(select(CompletedOrder).where(CompletedOrder.client == tg_id,
                                                                      CompletedOrder.mark_for_client)
                                         .order_by(CompletedOrder.date.desc())
                                         .limit(3)  # Ограничение до 10 заказов
                                         )
        # Получаем результаты запроса из statistics и вызываем scalars(),
        # чтобы получить скалярные значения (простые значения, а не кортежи).
        # Затем метод all() используется для извлечения всех результатов запроса.
        feedback = feedback.scalars().all()
        return feedback


# после успешной модерации разрешаем разработчику доступ к панели разработчика
async def add_developer_feedback(order_id, mark, feedback, total_feedbacks, mark_sum_about_client):
    async with async_session() as session:
        order = await session.scalar(select(CompletedOrder).where(CompletedOrder.id == order_id))
        client = await session.scalar(select(Client).where(Client.tg_id == order.client))
        client.rating = (mark_sum_about_client + int(mark))/(total_feedbacks+1)
        # обновляем данные
        await session.execute(update(CompletedOrder).where(CompletedOrder.id == order_id).values(
            mark_for_client=int(mark), feedback_about_client=feedback))
        await session.commit()


# после успешной модерации разрешаем разработчику доступ к панели разработчика
async def edit_developer_feedback(order_id, mark, feedback, total_feedbacks, mark_sum_about_client):
    async with async_session() as session:
        order = await session.scalar(select(CompletedOrder).where(CompletedOrder.id == order_id))
        client = await session.scalar(select(Client).where(Client.tg_id == order.developer))
        client.rating = ((mark_sum_about_client - order.mark_for_client) + int(mark))/(total_feedbacks)
        # обновляем данные
        await session.execute(update(CompletedOrder).where(CompletedOrder.id == order_id).values(
            mark_for_client=int(mark), feedback_about_client=feedback))
        await session.commit()


"""

Запросы администраторов к БД
----------------------------------------------------------------------------------------------
"""
# добавляем тарифа в БД
async def add_tariff(name, description, responses, amount):
    async with async_session() as session:
        session.add(Tariff(name=name, description=description, responses=responses,
                             amount=amount))
        await session.commit()


# добавляем тарифа в БД
async def edit_tariff(tariff_id ,name, description, responses, amount):
    async with async_session() as session:
        await session.execute(update(Tariff).where(Tariff.id == tariff_id).values(name=name, description=description,
                                                                                  responses=responses, amount=amount))
        await session.commit()


# удаляем определённый отклик из БД
async def delete_tariff(tariff_id):
    async with async_session() as session:
        tariff = await session.scalar(select(Tariff).where(Tariff.id == tariff_id))
        await session.delete(tariff)
        await session.commit()


# Берем всех пользователей из БД
async def all_users():
    async with async_session() as session:
        clients = await session.execute(select(Client))
        clients = clients.scalars().all()
        developers = await session.execute(select(Developer))
        developers = developers.scalars().all()
        recipients = clients + developers
        return recipients


# Берем всех пользователей из БД
async def all_clients():
    async with async_session() as session:
        # выбираем пользователя по его телеграмм id
        clients = await session.execute(select(Client))
        # Получаем результаты запроса из users и вызываем scalars(),
        # чтобы получить скалярные значения (простые значения, а не кортежи).
        # Затем метод all() используется для извлечения всех результатов запроса
        clients = clients.scalars().all()
        return clients


# Берем всех пользователей из БД
async def all_developers():
    async with async_session() as session:
        # выбираем пользователя по его телеграмм id
        developers = await session.execute(select(Developer))
        # Получаем результаты запроса из users и вызываем scalars(),
        # чтобы получить скалярные значения (простые значения, а не кортежи).
        # Затем метод all() используется для извлечения всех результатов запроса
        developers = developers.scalars().all()
        return developers


# Берем всех пользователей из БД
async def developers_with_subscription_end_date():
    async with async_session() as session:
        developers = await session.execute(select(Developer))
        developers = developers.scalars().all()
        developers = [
            developer for developer in developers
            if developer.subscription_end_date and
               developer.subscription_end_date.strftime('%d.%m.%Y') == datetime.datetime.now().strftime('%d.%m.%Y')
        ]
        return developers


# Берем всех пользователей из БД
async def developers_with_subscription():
    async with async_session() as session:
        developers = await session.execute(select(Developer).where(Developer.tariff))
        developers = developers.scalars().all()
        return developers

# Берем всех пользователей из БД
async def developers_without_subscription():
    async with async_session() as session:
        developers = await session.execute(select(Developer).where(Developer.tariff.is_(None)))
        developers = developers.scalars().all()
        return developers


# удаляем определённый отклик из БД
async def delete_subscription_for_tariff(developers):
    async with async_session() as session:
        for developer in developers:
            developer.tariff = None
            developer.subscription_end_date = None
            developer.responses = 0
            session.add(developer)
        await session.commit()


async def update_the_number_of_responses():
    async with async_session() as session:
        developers = await session.execute(select(Developer).where(Developer.tariff))
        developers = developers.scalars().all()
        for developer in developers:
            tariff = await session.scalar(select(Tariff).where(Tariff.id == developer.tariff))
            developer.responses = tariff.responses
        await session.commit()