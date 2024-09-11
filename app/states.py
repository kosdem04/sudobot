from aiogram.fsm.state import State, StatesGroup


class Register(StatesGroup):
    role = State()
    moderation = State()


"""

Состояния для клиентов
----------------------------------------------------------------------------------------------
"""
class ClientMenu(StatesGroup):
    menu = State()


class AddOrder(StatesGroup):
    title = State()
    description = State()
    sure = State()


class EditOrder(StatesGroup):
    title = State()
    description = State()
    sure = State()


class DeleteOrder(StatesGroup):
    sure = State()


class ClientOrder(StatesGroup):
    list = State()
    order = State()
    sure = State()


class FAQ(StatesGroup):
    client = State()
    developer = State()


"""

Состояния для разработчиков
----------------------------------------------------------------------------------------------
"""
class DeveloperMenu(StatesGroup):
    menu = State()


class DeveloperProfile(StatesGroup):
    profile = State()
    tariffs = State()
    pay_tariff = State()
