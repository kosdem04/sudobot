import datetime

from sqlalchemy import ForeignKey, String, BigInteger, DECIMAL
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

from config import DB_URL
from typing import List

engine = create_async_engine(url=DB_URL,
                             echo=True)
    
async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


# Таблица с администраторами
class Admin(Base):  # название для SqlAlchemy
    __tablename__ = 'admins'  # название для БД

    # прописываем характеристики полей
    tg_id: Mapped[int] = mapped_column(primary_key=True)
    user_name: Mapped[str] = mapped_column(String(100))


# Таблица заказчиков
class Client(Base):
    __tablename__ = 'clients'

    tg_id: Mapped[int] = mapped_column(primary_key=True)
    #username: Mapped[str] = mapped_column(String(100))
    rating = mapped_column(DECIMAL(3, 2), default=0)
    #name: Mapped[str] = mapped_column(String(100), default='client')

    # прописываем все отношения для таблицы

    # первичный ключ по отношению к таблице Order
    order_rel: Mapped[List["Order"]] = relationship(back_populates="client_rel", cascade='all, delete')
    # первичный ключ по отношению к таблице CompletedOrder
    completed_order_rel: Mapped[List["CompletedOrder"]] = relationship(back_populates="client_rel",
                                                                       cascade='all, delete')


# Таблица заказов заказчиков
class Order(Base):
    __tablename__ = 'orders'

    id: Mapped[int] = mapped_column(primary_key=True)
    client: Mapped[int] = mapped_column(ForeignKey('clients.tg_id', ondelete='CASCADE'))
    title: Mapped[str] = mapped_column(String(50))
    description: Mapped[str] = mapped_column(String(1000))
    date: Mapped[datetime.datetime]
    available: Mapped[bool] = mapped_column(default=False)

    # прописываем все отношения для таблицы

    # внешний ключ для таблицы
    client_rel: Mapped["Client"] = relationship(back_populates="order_rel")
    # первичный ключ по отношению к таблице Response
    response_rel: Mapped[List["Response"]] = relationship(back_populates="order_rel", cascade='all, delete')



# Таблица разработчиков
class Developer(Base):
    __tablename__ = 'developers'

    tg_id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(100))
    rating = mapped_column(DECIMAL(3, 2), default=0)
    responses: Mapped[int] = mapped_column(default=0)
    completed_orders: Mapped[int] = mapped_column(default=0)
    tariff: Mapped[int] = mapped_column(ForeignKey('tariffs.id', ondelete='CASCADE'), nullable=True)
    balance: Mapped[float] = mapped_column(default=0)
    moderation: Mapped[bool] = mapped_column(default=False)

    # прописываем все отношения для таблицы
    tariff_rel: Mapped["Tariff"] = relationship(back_populates="developer_rel")
    # первичный ключ по отношению к таблице Response
    response_rel: Mapped[List["Response"]] = relationship(back_populates="developer_rel", cascade='all, delete')
    # первичный ключ по отношению к таблице CompletedOrder
    completed_order_rel: Mapped[List["CompletedOrder"]] = relationship(back_populates="developer_rel",
                                                                       cascade='all, delete')



# Таблица тарифов для разработчиков
class Tariff(Base):
    __tablename__ = 'tariffs'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    responses: Mapped[int]
    description: Mapped[str] = mapped_column(String(1000))
    amount: Mapped[float] = mapped_column()

    # прописываем все отношения для таблицы

    # первичный ключ по отношению к таблице Developer
    developer_rel: Mapped[List["Developer"]] = relationship(back_populates="tariff_rel", cascade='all, delete')


# Таблица откликов
class Response(Base):
    __tablename__ = 'responses'

    id: Mapped[int] = mapped_column(primary_key=True)
    order: Mapped[int] = mapped_column(ForeignKey('orders.id', ondelete='CASCADE'))
    developer: Mapped[int] = mapped_column(ForeignKey('developers.tg_id', ondelete='CASCADE'))
    description: Mapped[str] = mapped_column(String(1000))
    status: Mapped[str] = mapped_column(String(50))

    # прописываем все отношения для таблицы
    order_rel: Mapped["Order"] = relationship(back_populates="response_rel")
    developer_rel: Mapped["Developer"] = relationship(back_populates="response_rel")


# Таблица выполненных заказов
class CompletedOrder(Base):
    __tablename__ = 'completed_orders'

    id: Mapped[int] = mapped_column(primary_key=True)
    client: Mapped[int] = mapped_column(ForeignKey('clients.tg_id', ondelete='CASCADE'))
    title: Mapped[str] = mapped_column(String(50))
    description: Mapped[str] = mapped_column(String(1000))
    developer: Mapped[int] = mapped_column(ForeignKey('developers.tg_id', ondelete='CASCADE'))
    date: Mapped[datetime.datetime]

    # прописываем все отношения для таблицы
    client_rel: Mapped["Client"] = relationship(back_populates="completed_order_rel")
    developer_rel: Mapped["Developer"] = relationship(back_populates="completed_order_rel")
    # первичный ключ по отношению к таблице FeedbackAboutClient
    feedback_about_client_rel: Mapped[List["FeedbackAboutClient"]] = relationship(back_populates="completed_order_rel",
                                                                                  cascade='all, delete')
    # первичный ключ по отношению к таблице FeedbackAboutDeveloper
    feedback_about_developer_rel: Mapped[List["FeedbackAboutDeveloper"]] = relationship(
        back_populates="completed_order_rel", cascade='all, delete')


# Таблица отзывов о заказчиках
class FeedbackAboutClient(Base):
    __tablename__ = 'feedback_about_clients'

    id: Mapped[int] = mapped_column(primary_key=True)
    completed_order: Mapped[int] = mapped_column(ForeignKey('completed_orders.id', ondelete='CASCADE'))
    description: Mapped[str] = mapped_column(String(1000))
    mark: Mapped[int]

    # прописываем все отношения для таблицы
    completed_order_rel: Mapped["CompletedOrder"] = relationship(back_populates="feedback_about_client_rel")


# Таблица отзывов о разработчиках
class FeedbackAboutDeveloper(Base):
    __tablename__ = 'feedback_about_developers'

    id: Mapped[int] = mapped_column(primary_key=True)
    completed_order: Mapped[int] = mapped_column(ForeignKey('completed_orders.id', ondelete='CASCADE'))
    description: Mapped[str] = mapped_column(String(1000))
    mark: Mapped[int]

    # прописываем все отношения для таблицы
    completed_order_rel: Mapped["CompletedOrder"] = relationship(back_populates="feedback_about_developer_rel")


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
