from abc import ABC, abstractmethod
from pyrogram import Client
from db.db_connect import AsyncDBConnect


class Handler(ABC):
    """Абстракция для хэндлеров"""

    def __init__(self, app: Client, db: AsyncDBConnect):
        self.app = app
        self.db = db

    @abstractmethod
    def register_handlers(self):
        """Метод для регистрации обработчиков"""
        pass
