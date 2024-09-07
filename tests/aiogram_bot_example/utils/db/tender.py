import sqlite3

from typing import Union, Optional

from utils import naming_columns
from utils.types import Tender, Complaint


class TenderDataBase:
    def __init__(self, db_name) -> None:
        self.conn = sqlite3.connect(db_name)
        self.cur = self.conn.cursor()
    
    def exist_tender(self, tender_id: str) -> bool:
        """
        Метод проверяет существование тендера в базе данных
        
        :param tender_id: Уникальный идентификатор тендера.

        :return: False, Не существует; True, существует
        """

        with self.conn:
            # Получение результата с базы данных
            res = self.cur.execute(
                "SELECT * FROM tenders WHERE id = ?",
                (tender_id,)
            ).fetchall()

        return bool(len(res))

    def add_tender(self, tender: Tender) -> None:
        with self.conn:
            self.cur.execute(
                "INSERT INTO tenders (id, name, url, deadline_date, deadline_time, customer_name, user_id, creation_date, status)"
                "VALUES (:id, :name, :url, :deadline_date, :deadline_time, :customer_name, :user_id, :creation_date, :status)",
                (tender.dict())
            )
            if tender.complaints:
                complaints = tender.complaints.split(";")
                for complaint in complaints:
                    self.add_complaint(tender_id=tender.id, url=complaint)

    @naming_columns(Tender)
    def get_tender(self, tender_id: str) -> Optional[Tender]:
        """
        Метод получения информации об тендере с базы данных.
        """
        with self.conn:
            # Получение результата с базы данных
            query = "SELECT tenders.*, GROUP_CONCAT(tender_complaints.url, ';') as complaints FROM tenders "\
                    "LEFT JOIN tender_complaints "\
                    "ON tender_complaints.tender_id = tenders.id "\
                    "WHERE tenders.id = ?"


            res = self.cur.execute(
                query,
                (tender_id,)
            ).fetchone()

        return res if any(res) else None

    def update_tender_status(self, tender_id: str, new_status: int):
        with self.conn:
            self.cur.execute(
                "UPDATE tenders SET status = ? WHERE id = ?",
                (new_status, tender_id,))

    @naming_columns(Tender)
    def get_tenders_by_status(self, status, offset=0) -> Optional[list[Tender]]:
        with self.conn:
            return self.cur.execute("SELECT * FROM tenders WHERE status = ? ORDER BY id DESC LIMIT 5 OFFSET ?", (status,offset,)).fetchall()

    def get_count_tenders_by_status(self, status: int) -> int:
        with self.conn:
            res = self.cur.execute("SELECT COUNT(*) FROM tenders WHERE status = ?", (status,)).fetchone()
            return res[0]

    @naming_columns(Tender)
    def get_tenders_check(self):
        with self.conn:
            query = "SELECT tenders.*, GROUP_CONCAT(tender_complaints.url, ';') as complaints FROM tenders "\
                    "JOIN tender_complaints "\
                    "ON tender_complaints.tender_id = tenders.id "\
                    "WHERE status in (1,2)"

            return self.cur.execute(query).fetchall()
        
    def update_tender_datetime(self, new_tender_info: Tender):
        with self.conn:
            self.cur.execute(
                "UPDATE tenders SET deadline_date = :deadline_date, deadline_time = :deadline_time WHERE id = :id",
                (new_tender_info.dict())
            )
    
    def delete_tender(self, tender_id: int):
        with self.conn:
            self.cur.execute("DELETE tenders WHERE id = ?", (tender_id,))

    def add_complaint(self, tender_id: int, url: str):
        with self.conn:
            self.cur.execute("INSERT INTO tender_complaints (url, tender_id) VALUES (?,?)", (url, tender_id,))