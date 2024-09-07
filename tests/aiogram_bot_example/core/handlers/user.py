import math

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command, CommandObject

from core.callback_data import TenderCall, PaginationCall
from core.keyboards import TenderKB
from core.filters import IsPrivateChat, IsGroupChat

from utils import other_tender
from utils.types import Tender, TenderStatus
from utils.db import DataBaseController
from utils.tender.tender_view import display_add_tender, display_list_tender


router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    """
    Обработчик команды /start
    """
    await message.answer("<b>Добро пожаловать в Тендер бот.</b>")

@router.message(IsGroupChat(), Command("добавить_тендер", "добавить", "д", "add"))
async def cmd_add_tender(message: Message, command: CommandObject, db: DataBaseController):
    try:
        # Получает URL тендера из команды
        tender_url = other_tender.get_command_args(command=command, is_url=True)

        # Получаем id тендера из ССЫЛКИ
        tender_id = other_tender.extract_id_from_url(tender_url)

        _exist_tender = db.tender.exist_tender(tender_id=tender_id)

        if _exist_tender:
            raise ValueError("Тендер уже существует в системе.")

        # Парсинг данных
        tender: Tender = await other_tender.tender_parser(tender_url)

        tender.id = tender_id
        tender.url = tender_url
        tender.user_id = message.from_user.id
        
        db.tender.add_tender(tender)
        tender_text = display_add_tender(tender)
        
        await message.answer(
            text=tender_text,
            reply_markup=TenderKB.confirm_add_tender(
                user_id=message.from_user.id,
                tender_id=tender_id
            )
        )
    except ValueError as Ex:
        print(Ex)
        await message.answer(f"⚠️ {Ex}")

    
@router.message(IsGroupChat(), Command("подал_заявку", "подать", "п", "accept"))
async def cmd_submitted_tender(message: Message, command: CommandObject, db: DataBaseController):
    try:
        # Получает URL тендера из команды
        tender_identification = other_tender.get_command_args(command=command)

        if tender_identification.startswith("https://"):
            # Получаем id тендера из ССЫЛКИ
            tender_id = other_tender.extract_id_from_url(tender_identification)
        else:
            tender_id = tender_identification

        tender: Tender = db.tender.get_tender(tender_id=tender_id)
        
        # Если тендер не существует
        if not tender:
            raise ValueError(f"Тендер №{tender.id} не существует системе.")
        
        if tender.status == TenderStatus.IN_SUB.value:
            raise ValueError(f"Тендер №{tender.id} находится на этапе <code>{TenderStatus.status_description.value.get(TenderStatus.IN_SUB.value)}</code>")

        db.tender.update_tender_status(tender_id=tender.id,new_status=TenderStatus.IN_SUB.value)

        await message.answer(f"Тендер №{tender.id} успешно переведен в статус <code>{TenderStatus.status_description.value[TenderStatus.IN_SUB.value]}</code>")
    except ValueError as Ex:
        await message.answer(f"⚠️ {Ex}")


@router.message(IsGroupChat(), Command("удалить_заявку", "у", "remove", "удалить"))
async def cmd_delete_tender(message: Message, command: CommandObject, db: DataBaseController):
    try:
        # Получает URL тендера из команды
        tender_identification = other_tender.get_command_args(command=command)

        if tender_identification.startswith("https://"):
            # Получаем id тендера из ССЫЛКИ
            tender_id = other_tender.extract_id_from_url(tender_identification)
        else:
            tender_id = tender_identification

        tender: Tender = db.tender.get_tender(tender_id=tender_id)
        
        # Если тендер не существует
        if not tender:
            raise ValueError(f"Тендер №{tender.id} не существует системе.")
        
        if tender.status == TenderStatus.DELETE.value:
            raise ValueError(f"Тендер №{tender.id} находится на этапе <code>{TenderStatus.status_description.value.get(TenderStatus.DELETE.value)}</code>")

        db.tender.update_tender_status(tender_id=tender.id,new_status=TenderStatus.DELETE.value)

        await message.answer(f"Тендер №{tender.id} успешно переведен в статус <code>{TenderStatus.status_description.value[TenderStatus.DELETE.value]}</code>")
    except ValueError as Ex:
        await message.answer(f"⚠️ {Ex}")


# Обработка команд по выводу списка тендеров по статусу заказа.
@router.message(IsPrivateChat(), Command("remove_list", "sub_list", "jobs_list"))
async def cmd_get_tenders_list(message: Message, command: CommandObject, db: DataBaseController):
    try:
        # Получение команды.
        command = command.command

        # Получение данных команды
        command_data = eval(f"TenderStatus.{command}.value")
        command_status = command_data.get("status")
        command_text = command_data.get("tender_text")

        pages = db.tender.get_count_tenders_by_status(command_status)
        max_pager = math.ceil(pages/5)

        # Получение списка тендеров по статусу команды.
        tenders = db.tender.get_tenders_by_status(command_status)

        # Генерация шаблона для вывода пользователю
        template = display_list_tender(tenders, command_text)

        # Вывод шаблона пользователю
        await message.answer(f"{template}", reply_markup=TenderKB.pagination(command=command, max_page=max_pager))
    except ValueError as Ex:
        await message.answer(f"⚠️ {Ex}")


@router.callback_query(TenderCall.filter(F.action.in_(["accept", "cancel"])))
async def callback_new_task(call: CallbackQuery, callback_data: TenderCall, db: DataBaseController):
        try:
            action = callback_data.action
            tender_id = callback_data.tender_id
            tender_user_id = callback_data.cr_user_id
            
            if call.from_user.id != tender_user_id:
                raise ValueError("Нельзя подтверждать тендер, который принадлежит другому пользователю.")
            
            if action == "accept":
                db.tender.update_tender_status(tender_id=tender_id, new_status=1)
                text = "✅ Тендер успешно добавлен в систему."
            elif action == "cancel":
                db.tender.delete_tender(tender_id=tender_id)
                text = "❌ Тендер отменен."
            else:
                raise ValueError("Не знаю как ты попал сюда, сообщи админу.")
                
            await call.message.edit_text(f"<b>{text}</b>")
            
        except ValueError as Ex:
            await call.answer(show_alert=True, text=str(Ex))


# Обработка пагинации
@router.callback_query(PaginationCall.filter())
async def cmd_get_tenders_list(call: CallbackQuery, callback_data: PaginationCall, db: DataBaseController):
    try:
        # Получение команды.
        command = callback_data.command
        page = callback_data.page

        # Получение данных команды
        command_data = eval(f"TenderStatus.{command}.value")
        command_status = command_data.get("status")
        command_text = command_data.get("tender_text")

        pages = db.tender.get_count_tenders_by_status(command_status)

        max_pager = math.ceil(pages/5)

        # Получение списка тендеров по статусу команды.
        tenders = db.tender.get_tenders_by_status(command_status, offset=page*5)

        # Генерация шаблона для вывода пользователю
        template = display_list_tender(tenders, command_text)

        # Вывод шаблона пользователю
        await call.message.edit_text(f"{template}", reply_markup=TenderKB.pagination(command=command, max_page=max_pager, current_page=page))
    except ValueError as Ex:
        await call.message.edit_text(f"⚠️ {Ex}")


@router.message(Command("id"))
async def cmd_id(message: Message):
    await message.delete()
    print(message.chat)


@router.message(Command("menu"))
@router.message(F.text.in_(["🎛 Меню"]))
async def cmd_id(message: Message, command: CommandObject):
    args = command.args
    if not args:
        return 


