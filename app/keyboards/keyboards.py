from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    KeyboardButton,
    ReplyKeyboardMarkup,
)


def get_inline_menu():
    """Inline клавиатура для работы я задачами"""
    buttons = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "Создание новой задачи", callback_data="create_tasks"
                )
            ],
            [
                InlineKeyboardButton(
                    "Просмотр активных задач", callback_data="active_tasks"
                )
            ],
            [InlineKeyboardButton("Просмотр завершённых", callback_data="done_tasks")],
        ]
    )
    return buttons


def get_register_menu():
    """Клавиатура для регистрации"""
    keyboard = [[KeyboardButton("Регистрация")]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
