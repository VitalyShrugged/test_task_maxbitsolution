from app.handlers.abstract_handler import Handler
from app.keyboards.keyboards import get_inline_menu
from app.fsm import TaskFSM, task_fsm
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup


class CallbackHandler(Handler):
    """Регистрация хэндлеров для обработки callback сообщений"""

    def register_handlers(self):
        @self.app.on_callback_query(filters.regex("delete_task_"))
        async def delete_task_callback(
            client: Client, callback_query: CallbackQuery
        ) -> None:
            """Обработка callback для удаления задачи"""
            task_id = callback_query.data.split("_")[2]
            await self.db.execute_query("DELETE FROM tasks WHERE id = $1", int(task_id))
            await callback_query.message.reply(
                "Задача успешно удалена.", reply_markup=get_inline_menu()
            )

        @self.app.on_callback_query(filters.regex("done_task_"))
        async def ready_task_callback(
            client: Client, callback_query: CallbackQuery
        ) -> None:
            """Обработка callback для изменения статуса задачи"""
            task_id = callback_query.data.split("_")[2]
            callback_data = callback_query.data.split("_")[3]
            if callback_data == "reload":
                await self.db.fetch_query(
                    "UPDATE tasks SET is_done = FALSE WHERE id = $1", int(task_id)
                )
                await callback_query.message.reply(
                    "Задача снова выполняется!.", reply_markup=get_inline_menu()
                )
            else:
                await self.db.fetch_query(
                    "UPDATE tasks SET is_done = TRUE WHERE id = $1", int(task_id)
                )
                await callback_query.message.reply(
                    "Задача помечена как выполненная.", reply_markup=get_inline_menu()
                )

        @self.app.on_callback_query(
            filters.regex("done_tasks") | filters.regex("active_tasks")
        )
        async def tasks_callback(client: Client, callback_query: CallbackQuery) -> None:
            """Обработка callback для просмотра активных и завершённых задач"""
            callback_data = callback_query.data
            user_id = callback_query.from_user.id
            if callback_data == "active_tasks":
                tasks = await self.db.fetch_query(
                    "SELECT * FROM tasks WHERE user_id = $1 AND is_done = FALSE",
                    int(user_id),
                )
            else:
                tasks = await self.db.fetch_query(
                    "SELECT * FROM tasks WHERE user_id = $1 AND is_done = TRUE",
                    int(user_id),
                )
            if tasks:
                buttons = []
                for task in tasks:
                    task_status = "Завершена" if task["is_done"] else "Выполняется"
                    buttons.append(
                        [
                            InlineKeyboardButton(
                                text=f"Название -- {task['title']}\n  статус -- {task_status}",
                                callback_data=f"task_{task['id']}",
                            )
                        ]
                    )

                keyboard = InlineKeyboardMarkup(buttons)
                await callback_query.message.reply(
                    text="Ваши задачи: ", reply_markup=keyboard
                )
            else:
                await callback_query.message.reply(text="Задачи не найдены.")

        @self.app.on_callback_query(filters.regex("task_"))
        async def handle_task_callback(client: Client, callback_query) -> None:
            """Обработка callback для просмотра задачи"""
            task_id = callback_query.data.split("_")[1]
            task = await self.db.fetch_query(
                "SELECT * FROM tasks WHERE id = $1 ", int(task_id)
            )

            if task:
                task_info = f"Название: {task[0]['title']}\nОписание: {task[0]['description']}\nСтатус: {task[0]['is_done']}"
                keyboard = InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text=(
                                    "Возобновить"
                                    if task[0]["is_done"]
                                    else "Пометить выполненной"
                                ),
                                callback_data=f"done_task_{task_id}_{'reload' if task[0]['is_done'] else 'done'}",
                            )
                        ],
                        [
                            InlineKeyboardButton(
                                "Удалить", callback_data=f"delete_task_{task_id}"
                            ),
                        ],
                        [
                            InlineKeyboardButton(
                                "Вернуться в меню", callback_data="back_to_menu"
                            )
                        ],
                    ]
                )
                await callback_query.message.reply(
                    text=task_info, reply_markup=keyboard
                )
            else:
                await callback_query.message.reply(text="Задача не найдена.")

        @self.app.on_callback_query()
        async def handle_callback(
            client: Client, callback_query: CallbackQuery
        ) -> None:
            """Обработка callback для меню"""
            user_id = callback_query.from_user.id
            callback_data = callback_query.data
            if callback_data == "create_tasks":
                task_fsm[user_id] = TaskFSM(user_id)
                task_fsm[user_id].show_menu()
                task_fsm[user_id].create_task()
                await callback_query.message.edit_text("Введите заголовок задачи:")
            elif callback_data == "back_to_menu":
                await callback_query.message.reply(
                    "Главное меню!.", reply_markup=get_inline_menu()
                )
