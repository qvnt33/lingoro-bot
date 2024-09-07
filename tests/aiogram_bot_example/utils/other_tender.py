from aiogram.filters import CommandObject

from utils.types import Tender
from utils.tender.parse import Notice223, Notice44

def extract_id_from_url(url: str) -> str:
    position_number = url.find("=")+1
    tender_order = url[position_number:].replace("#", "")
    return tender_order

def get_command_args(command: CommandObject, is_url: bool=False) -> str:
    cmd_args = command.args

    # Если нет переданных аргументов вернуть ошибку
    if not cmd_args:
        raise ValueError("Введите URL после команды." if is_url else "Введите URL или номер тендера после команды.")
        
    # Если нужно проверить ссылка или нет 
    if is_url:
        if not cmd_args.startswith("https://"):
            raise ValueError("Введите корректный URL после команды.")
        # Заменяем # на пустоту
        cmd_args = cmd_args.replace("#", "")

    return cmd_args

async def tender_parser(tender_url: str) -> Tender:
    # Фз 223
    if "noticeInfoId=" in tender_url:
        data: dict | None = await Notice223(tender_url).parse()
    # Фз 44
    elif "regNumber=" in tender_url:
        data: dict | None = await Notice44(tender_url).parse()
    else:
        raise ValueError("Введите корректный URL после команды.")
    
    return Tender(**data)


