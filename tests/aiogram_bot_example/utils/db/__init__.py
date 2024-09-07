from .tender import TenderDataBase


class DataBaseController:
    def __init__(self, db_name: str) -> None:
        self.tender = TenderDataBase(db_name)
        