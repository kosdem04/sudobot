import asyncio, logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.client import client
from app.developer import developer
from app.admin import admin
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.apshed import check_subscription_end_date, update_the_number_of_responses
from config import TOKEN

from app.database.models import async_main


async def main():
    bot = Bot(token=TOKEN,
              default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    
    dp = Dispatcher()
    dp.include_routers(client, developer, admin)
    dp.startup.register(startup)
    dp.shutdown.register(shutdown)

    """

    Создаём ежедневно повторяющиеся действия
    ----------------------------------------------------------------------------------------------
    """

    # создаём объект расписания с установкой часового пояса (scheduler)
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    # sheduler = AsyncIOScheduler(timezone="Asia/Novosibirsk")

    # варианты добавления задач, которые сработают через минуту и 2 минуты соответсвенно

    # sheduler.add_job(delete_rent, trigger='cron', hour=datetime.now().hour, minute=datetime.now().minute+1,
    # start_date=datetime.now(), kwargs={'bot': bot})
    # sheduler.add_job(notifications, trigger='cron', hour=datetime.now().hour, minute=datetime.now().minute + 2,
    # start_date=datetime.now(), kwargs={'bot': bot})

    # добавляем задачи и устанавливаем нужный час и минуту, при наступлении которых задачи будут срабатывать
    # задача для удаления аренды с истёкшим сроком
    # sheduler.add_job(delete_rent, trigger='cron', hour=14, minute=55,
    # start_date=datetime.now(), kwargs={'bot': bot})
    scheduler.add_job(check_subscription_end_date, trigger='cron', hour=16, minute=37, kwargs={'bot': bot})
    # задача для уведомления пользователей, что до окончания аренды остался 1 день
    scheduler.add_job(update_the_number_of_responses, trigger='cron', hour=16, minute=18, kwargs={'bot': bot})
    # sheduler.add_job(notifications, trigger='cron', hour=18, minute=56,
    # start_date=datetime.now(), kwargs={'bot': bot})
    scheduler.start()  # запускаем планировщик
    
    await dp.start_polling(bot)


async def startup(dispatcher: Dispatcher):
    await async_main()
    print('Starting up...')


async def shutdown(dispatcher: Dispatcher):
    print('Shutting down...')


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)  # Логгирование
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
