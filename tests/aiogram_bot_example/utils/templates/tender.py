from utils.types import Tender



class TenderView:
    @staticmethod
    def display_add_tender(tender: Tender) -> str:
        """
        Метод вывода информации перед добавлением тендера в базу данных.

        :param tender: Объект тендера.

        :return: Готовый шаблон для вывода тендера
        """

        template = (
            f"<b>📝Добавление нового тендера:</b>\n"
            f"\t<b>├ Реестровый номер</b> <code>{tender.id}</code>\n"
            f"\t<b>├ Заказчик:</b> <code>{tender.customer_name}</code>\n"
            f"\t<b>├ Наименование:</b> <code>{tender.name}</code>\n"
            f"\t<b>└ Срок окончания:</b> <code>{tender.deadline_date} {tender.deadline_time}</code>\n"
        )
        
        # Проверка наличия жалоб
        if tender.complaints:
            # Формирование текста с жалобами и добавляем его
            template += TenderView.generate_complaint_text(tender.complaints)
        
        return template
        
        return template
    
    @staticmethod
    def display_tender(tender: Tender):
        template = (
            f"<b>📝Тендер №<code>{tender.id}<code></b>\n"
            f"\t<b>├ Заказчик:</b> <code>{tender.customer_name}</code>\n"
            f"\t<b>├ Наименование:</b> <code>{tender.name}</code>\n"
            f"\t<b>├ Дата исполнения: </b> <code>{tender.deadline_date}</code>\n"
            f"\t<b>└ Срок окончания: </b> <code>{tender.deadline_time}</code>\n"
            # f"\t<b> Время добавления:</b> <code>{tender.creation_date}</code>\n"
        )
        
        # Проверка наличия жалоб
        if tender.complaints:
            # Формирование текста с жалобами и добавляем его
            template += TenderView.generate_complaint_text(tender.complaints)

        return template
    
    @staticmethod
    def display_tender_date_change_info(old_tender_info: Tender, new_tender_info: Tender) -> str:
        """
        Метод формирует текст для отображения информации об изменении даты подачи заявок на тендер.
        """
        template = (
            f"<b>⚠️ Изменилась дата окончания приема заявок.</b>\n"\
            f"\n"
            f"<b>{' ':5}➡️ <a href='{old_tender_info.url}'>{old_tender_info.name}</a></b>\n"
            f"\n"
            f"<b>{' ':5}⭕️ Старая дата: <code>{old_tender_info.deadline_date} {old_tender_info.deadline_time}</code></b>\n"
            f"\n"
            f"<b>{' ':5}❇️ Новая дата: <code>{new_tender_info.deadline_date} {new_tender_info.deadline_time}</code></b>\n"
        )

        return template

    @staticmethod
    def display_tender_new_complaint(tender: Tender, complaints: list[str]):
        template = (
            f"<b>⚠️ Поступили новые жалобы</b>\n"
            f"\n"
            f"<b>{' ':5}➡️ <a href='{tender.url}'>{tender.name}</a></b>\n"
            f"<b>{' ':5}📅 Срок окончания: <code>{tender.deadline_date} {tender.deadline_time}</code></b>\n"
            f"\n"
            +TenderView.generate_complaint_text(complaints, is_attention=False)
        )

        return template

    @staticmethod
    def generate_complaint_text(complaints: str, is_attention: bool = True) -> str:
            """
            Метод формирует текст с жалобами
            """

            if isinstance(complaints, str):
                # Разбиваем тендеры.
                complaints = complaints.split(";")
            template = ""
            if is_attention:
                template = "\n<b>❗️Обратите внимание</b>\n\n"
            template += "\n".join(
                f"{' '*5}<b><a href='{complaint}'>⛔️ Жалоба #{num}</a></b>"
                for num, complaint in enumerate(complaints, start=1)
            )

            return template









