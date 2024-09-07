from utils.types import Tender


def display_add_tender(tender: Tender):
    
    text = (
        f"<b>📝Добавление нового тендера:</b>\n"
        f"{' '*5}<b>├ Реестровый номер</b> <code>{tender.id}</code>\n"
        f"{' '*5}<b>├ Заказчик:</b> <code>{tender.customer_name}</code>\n"
        f"{' '*5}<b>├ Наименование:</b> <code>{tender.name}</code>\n"
        f"{' '*5}<b>└ Срок окончания:</b> <code>{tender.deadline_date} {tender.deadline_time}</code>\n"
    )
    print(tender)
    if tender.complaints:
        complaint_text = "<b>❗️Обратите внимание</b>\n\n"
        complaints = tender.complaints.split(";")
        for num, complaint in enumerate(complaints, start=1):
            complaint_text += f"{' '*5}<b><a href='{complaint}'>⛔️ Жалоба #{num}</a></b>\n"
        text += complaint_text

    return text

def display_list_tender(items: list, text_value: str) -> str:
    """
    Создает список из списка словарей и добавляет его к существующему тексту.
    """
    if not items:
        raise ValueError(text_value)
    text = ""
    for item in items:  # type: dict
        item: Tender
        text += f"➡️ <a href='{item.url}'>{item.name}</a>\n"
    return text