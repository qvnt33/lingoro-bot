import enum

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Union

from .base import BaseModel

@dataclass
class Complaint(BaseModel):
    id: Optional[str] = None
    url: Optional[str] = None
    tender_id: Optional[str] = None
    creation_date: Union[datetime, str, None] = datetime.now().replace(microsecond=0)

@dataclass
class Tender(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    url: Optional[str] = None
    status: int = 0
    deadline_date: Optional[str] = None
    deadline_time: Optional[str] = None
    customer_name: Optional[str] = None
    user_id: Optional[int] = None
    creation_date: Union[datetime, str, None] = datetime.now().replace(microsecond=0)
    
    # Связь с жалобами
    complaints: Optional[str] = None


class TenderStatus(enum.Enum):
    ADD = 1
    IN_JOBS = 1
    IN_SUB = 2
    DELETE = 3
    COMPLETED = 9

    status_description = {
        ADD: "Добавлен",
        IN_JOBS: "В работе",
        IN_SUB: "Заявка подана",
        DELETE: "Удален",
        COMPLETED: "Завершен",
    } 
    
    remove_list = {
        'description': 'Удаление тендера из списка',
        'status': DELETE,
        'tender_text': 'В данный момент нет удаленных тендеров.',
    }
    sub_list = {
        'description': 'Показать поданные заявки',
        'status': IN_SUB,
        'tender_text': 'В данный момент нет поданных заказов на тендеры.',
    }
    jobs_list = {
        'description': 'Показать список в работе.',
        'status': IN_JOBS,
        'tender_text': 'В данный момент нет тендеров в работе.',
    }

