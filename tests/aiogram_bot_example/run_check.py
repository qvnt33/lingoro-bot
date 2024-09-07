import time
import asyncio

from aiogram import Bot

from utils import other_tender
from utils.db import TenderDataBase
from utils.types import Tender
from utils.templates import TenderView


async def main():
    db = TenderDataBase("database.sqlite")
    bot = Bot(token="", parse_mode="HTML")

    while True:
        time.sleep(5)
        # Получаем все отслеживаемые тендеры.
        tenders = db.get_tenders_check()
        for old_tender_info in tenders:
            old_tender_info = db.get_tender(old_tender_info.id)

            # Получение новой информации об тендере
            new_tender_info: Tender = await other_tender.tender_parser(old_tender_info.url)
            new_tender_info.id = old_tender_info.id
            # Проверяем изменилась ли дата
            if old_tender_info.deadline_date != new_tender_info.deadline_date or old_tender_info.deadline_time != new_tender_info.deadline_time:
                db.update_tender_datetime(new_tender_info=new_tender_info)

                # Генерирует шаблона для отправки
                template_text = TenderView.display_tender_date_change_info(
                    old_tender_info=old_tender_info,
                    new_tender_info=new_tender_info
                )

                # Отправка сообщения пользователю добавивший тендер
                try:
                    await bot.send_message(
                        chat_id=old_tender_info.user_id,
                        text=template_text
                    )
                except:
                    pass

                # Отправка сообщения в чат.        
                try:
                    await bot.send_message(
                        chat_id=,
                        text=template_text
                    )
                except:
                    pass
            
            # Получение новых и старых жалоб
            new_complaints = new_tender_info.complaints.split(";") if new_tender_info.complaints else []     
            old_complaints = old_tender_info.complaints.split(";") if old_tender_info.complaints else []

            print(new_complaints, old_complaints)
            # Проверка добавились новые жалобы или нет
            if len(new_complaints) != len(old_complaints):
                # Проверяем какие новые жалобы появились
                new_arr = []
                for complaint in new_complaints:
                    if complaint not in old_complaints:
                        new_arr.append(complaint)
                        db.add_complaint(new_tender_info.id, complaint)
                
                # Генерирует шаблон для отправки
                template_text = TenderView.display_tender_new_complaint(
                    tender=old_tender_info,
                    complaints=new_arr
                )

                # Отправка сообщения пользователю добавивший тендер
                try:
                    await bot.send_message(
                        chat_id=old_tender_info.user_id,
                        text=template_text
                    )
                except:
                    pass

                # Отправка сообщения в чат.        
                try:
                    await bot.send_message(
                        chat_id=,
                        text=template_text
                    )
                except:
                    pass

if __name__ == "__main__":
    asyncio.run(main())