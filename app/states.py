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


class ClientProfile(StatesGroup):
    profile = State()


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
    total_pages = State()
    order = State()
    sure = State()


class ClientResponse(StatesGroup):
    list = State()
    order_responses = State()
    response_info = State()
    sure_complete_order = State()


class OrderHistory(StatesGroup):
    list = State()
    order_info = State()


class ClientCreateFeedback(StatesGroup):
    mark = State()
    feedback = State()
    sure = State()


class ClientEditFeedback(StatesGroup):
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
    total_pages = State()
    order_info = State()
    make_response = State()


class DeveloperResponse(StatesGroup):
    list = State()
    response_info = State()
    delete_response = State()


class CompletedOrder(StatesGroup):
    list = State()
    order_info = State()
    sure_complete_order = State()


class DeveloperCreateFeedback(StatesGroup):
    mark = State()
    feedback = State()
    sure = State()


class DeveloperEditFeedback(StatesGroup):
    mark = State()
    feedback = State()
    sure = State()