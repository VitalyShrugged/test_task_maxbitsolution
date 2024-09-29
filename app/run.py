import logging
from app.handlers.message_handler import MessageHandler
from app.handlers.callback_handler import CallbackHandler
from config.config import API_ID, API_HASH, BOT_TOKEN
from db.db_connect import AsyncDBConnect

from pyrogram import Client


app = Client(
    "my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN, in_memory=True
)
db = AsyncDBConnect()

logging.basicConfig(level=logging.INFO)

message_handler = MessageHandler(app=app, db=db)
callback_handler = CallbackHandler(app=app, db=db)

message_handler.register_handlers()
callback_handler.register_handlers()
