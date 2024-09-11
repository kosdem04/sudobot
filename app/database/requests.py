from app.database.models import async_session
from app.database.models import *
from sqlalchemy import select, update, delete, desc



"""

Запросы клиентов к БД
----------------------------------------------------------------------------------------------
"""
async def is_client(tg_id):
    async with async_session() as session:
        return True if await session.scalar(select(Client).where(Client.tg_id == tg_id)) else False

async def add_client(tg_id):
    async with async_session() as session:
        session.add(Client(tg_id=tg_id))
        await session.commit()


async def get_client(tg_id):
    async with async_session() as session:
        return await session.scalar(select(Client).where(Client.tg_id == tg_id))


async def client_orders(tg_id):
    async with async_session() as session:
        orders = await session.execute(select(Order).where(Order.client == tg_id, Order.available == True))
        # Получаем результаты запроса из statistics и вызываем scalars(),
        # чтобы получить скалярные значения (простые значения, а не кортежи).
        # Затем метод all() используется для извлечения всех результатов запроса.
        orders = orders.scalars().all()
        return orders


async def add_order(client, title, description):
    async with async_session() as session:
        order = Order(client=client, title=title, description=description, date=datetime.datetime.now())
        session.add(order)
        await session.commit()
        await session.refresh(order)
        return order


async def available_order(order_id):
    async with async_session() as session:
        order = await session.scalar(select(Order).where(Order.id == order_id))
        order.available = True
        await session.commit()
        await session.refresh(order)
        return order


async def delete_order(order_id):
    async with async_session() as session:
        order = await session.scalar(select(Order).where(Order.id == order_id))
        await session.delete(order)
        await session.commit()
        return order


async def get_order(order_id):
    async with async_session() as session:
        return await session.scalar(select(Order).where(Order.id == order_id))


async def edit_order(order_id, title, description):
    async with async_session() as session:
        await session.execute(update(Order).where(Order.id == order_id).values(title=title, description=description))
        await session.commit()


"""

Запросы разработчиков к БД
----------------------------------------------------------------------------------------------
"""
async def is_developer(tg_id):
    async with async_session() as session:
        return True if await session.scalar(select(Developer).where(Developer.tg_id == tg_id,
                                                                    Developer.moderation == True)) else False


async def get_developer(tg_id):
    async with async_session() as session:
        return await session.scalar(select(Developer).where(Developer.tg_id == tg_id))


async def is_moderation_developer(tg_id):
    async with async_session() as session:
        return True if await session.scalar(select(Developer).where(Developer.tg_id == tg_id,
                                                                    Developer.moderation == False)) else False

async def add_developer(tg_id, username):
    async with async_session() as session:
        session.add(Developer(tg_id=tg_id, username=username))
        await session.commit()


async def developer_activate(developer_id):
    async with async_session() as session:
        developer = await session.scalar(select(Developer).where(Developer.tg_id == developer_id))
        developer.moderation = True
        await session.commit()
        await session.refresh(developer)
        return developer


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


async def get_tariff(tariff_id):
    async with async_session() as session:
        return await session.scalar(select(Tariff).where(Tariff.id == tariff_id))


async def tariff_payed(developer_id, tariff):
    async with async_session() as session:
        await session.execute(update(Developer).where(Developer.tg_id == developer_id).values(
            responses=tariff.responses, tariff=tariff.id))
        await session.commit()