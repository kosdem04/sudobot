from app.database.models import async_session
from aiogram import Bot
import app.database.requests as db
from config import ADMINS
import datetime

# Ищем все записи, у которых срок аренды заканчивается сегодня и удаляем их
async def check_subscription_end_date(bot: Bot):
    async with async_session() as session:
        # конструкция try except ловит и выводит сообщение об ошибке,
        # а также не даёт им остановить работу программы
        #try:
            developer_with_subscription_end_date = await db.developers_with_subscription_end_date()
            # получаем список всех свободных ботов
            # получаем количество всех свободных ботов
            all_developers = await db.all_developers()
            # отчёты для администраторов

            # если заканчивающихся аренд нет
            if not developer_with_subscription_end_date:
                developer_with_subscription = await db.developers_with_subscription()
                developer_without_subscription = await db.developers_without_subscription()
                for admin in ADMINS:
                    await bot.send_message(admin, f'<b>{datetime.datetime.now().strftime('%d.%m.%Y')}|</b> Отсутствуют разработчики '
                                                  f'с закончившемся сроком действия тарифа\n\n'
                                                  f'Количество разработчиков, у которых есть подписка на тариф'
                                                  f' — <b>{len(developer_with_subscription)}</b>\n\n'
                                                  f'Количество разработчиков, у которых нет подписки на тариф'
                                                  f' — <b>{len(developer_without_subscription)}</b>\n\n'
                                                  f'Общее число разработчиков — <b>{len(all_developers)}</b>')
            else:
                await db.delete_subscription_for_tariff(developer_with_subscription_end_date)
                developer_with_subscription = await db.developers_with_subscription()
                developer_without_subscription = await db.developers_without_subscription()
                for admin in ADMINS:
                    await bot.send_message(admin,
                                           f'<b>{datetime.datetime.now().strftime('%d.%m.%Y')}|</b> Разработчиков '
                                           f'с закончившемся сроком действия тарифа — <b>{len(developer_with_subscription_end_date)}</b>\n\n'
                                           f'Количество разработчиков, у которых есть подписка на тариф'
                                           f' — <b>{len(developer_with_subscription)}</b>\n\n'
                                           f'Количество разработчиков, у которых нет подписки на тариф'
                                           f' — <b>{len(developer_without_subscription)}</b>\n\n'
                                           f'Общее число разработчиков — <b>{len(all_developers)}</b>')
        #except Exception:
            #for admin in ADMINS:
               # await bot.send_message(admin, f'{datetime.datetime.now().strftime('%d.%m.%Y')}'
                                              #f'| При проверке окончания тарифов произошла ошибка')


# Ищем всех пользователей, у номеров которых заканчивается срок аренды и уведомляем их
async def update_the_number_of_responses(bot: Bot):
    async with async_session() as session:
        # конструкция try except ловит и выводит сообщение об ошибке,
        # а также не даёт им остановить работу программы
        try:
            await db.update_the_number_of_responses()
            # отправляем всем администраторам отчёт о выполненной работе
            for admin in ADMINS:
                await bot.send_message(admin, f'Обновление количества откликов на '
                                              f'{datetime.datetime.now().strftime('%d.%m.%Y')} произошло успешно')
        except Exception:
            for admin in ADMINS:
                await bot.send_message(admin, f'При обновление количества откликов на '
                                              f'{datetime.datetime.now().strftime('%d.%m.%Y')} произошла ошибка')
