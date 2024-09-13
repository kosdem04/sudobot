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


class ClientResponse(StatesGroup):
    list = State()
    order_responses = State()
    sure_complete_order = State()


class OrderHistory(StatesGroup):
    list = State()
    order_responses = State()
    sure_complete_order = State()


class ClientFeedback(StatesGroup):
    list = State()
    developer = State()


class ClientCreateFeedback(StatesGroup):
    select_order = State()
    mark = State()
    feedback = State()
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


class Market(StatesGroup):
    list = State()
    order_info = State()
    make_response = State()


class DeveloperResponse(StatesGroup):
    list = State()
    delete_response = State()


class CompletedOrder(StatesGroup):
    list = State()
    order_info = State()
    sure_complete_order = State()