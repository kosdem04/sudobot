from app.database.models import async_session
from app.database.models import *
from sqlalchemy import select, update, delete, desc



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
        orders = await session.execute(select(Order).where(Order.client == tg_id, Order.available == True))
        # Получаем результаты запроса из statistics и вызываем scalars(),
        # чтобы получить скалярные значения (простые значения, а не кортежи).
        # Затем метод all() используется для извлечения всех результатов запроса.
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
        await session.delete(order)
        await session.commit()
        return order


# берём данные конкретного заказа
async def get_order(order_id):
    async with async_session() as session:
        return await session.scalar(select(Order).where(Order.id == order_id))

# изменение данных о закае
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


# после успешной модерации разрешаем разработчику доступ к панели разработчика
async def refuse_response(response_id):
    async with async_session() as session:
        await session.execute(update(Response).where(Response.id == response_id).values(status='Отказано'))
        await session.commit()


# берём данные о конкретном отклике
async def get_response(response_id):
    async with async_session() as session:
        return await session.scalar(select(Response).where(Response.id == response_id))

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
        return await session.scalar(select(Developer).where(Developer.tg_id == tg_id))


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
            responses=tariff.responses, tariff=tariff.id))
        await session.commit()


# Отображение всех заказов
async def all_orders():
    async with async_session() as session:
        orders = await session.execute(select(Order).where(Order.available == True))
        # Получаем результаты запроса из statistics и вызываем scalars(),
        # чтобы получить скалярные значения (простые значения, а не кортежи).
        # Затем метод all() используется для извлечения всех результатов запроса.
        orders = orders.scalars().all()
        return orders


# добавление нового отклика на заказ
async def add_response(developer_id, order_id, description):
    async with async_session() as session:
        session.add(Response(developer=developer_id, order=order_id, description=description,
                             status='На рассмотрении у заказчика'))
        await session.commit()


async def is_response_from_developer(developer_id):
    async with async_session() as session:
        return True if await session.scalar(select(Response).where(Response.developer == developer_id)) else False


# удаляем определённый заказ из БД
async def delete_response(response_id):
    async with async_session() as session:
        response = await session.scalar(select(Response).where(Response.id == response_id))
        await session.delete(response)
        await session.commit()



