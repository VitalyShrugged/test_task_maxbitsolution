from app.handlers.abstract_handler import Handler
from app.keyboards.keyboards import get_inline_menu, get_register_menu
from app.fsm import UserFSM, user_fsm, task_fsm
from pyrogram import Client, filters
from pyrogram.types import Message
import bcrypt

from app.service import check_password


class MessageHandler(Handler):
    """Класс для регистрации и обработки сообщений бота.

    Атрибуты:
        app (Client): экземпляр клиента Pyrogram.
        db (AsyncDBConnect): экземпляр подключения к базе данных.
    """
    
    def register_handlers(self):
        @self.app.on_message(filters.command("start"))
        async def start_command(client: Client, message: Message) -> None:
            """Обработчик команды start"""
            await self.db.create_tables()
            user_id = message.from_user.id
            existing_user = await self.db.fetch_query(
                "SELECT * FROM users WHERE user_id = $1", user_id
            )
            if not existing_user:
                user_fsm[user_id] = UserFSM(user_id)
                user_fsm[user_id].start()
                await message.reply(
                    "Привет! Для продолжения необходимо пройти регистрацию(Нажмите на кнопку Регистрация)",
                    reply_markup=get_register_menu(),
                )
            else:
                await message.reply("С возвращением!", reply_markup=get_inline_menu())

        @self.app.on_message(filters.command("register"))
        async def register_command(client: Client, message: Message) -> None:
            """Обработчик команды register"""
            user_id = message.from_user.id
            if user_id not in user_fsm:
                user_fsm[user_id] = UserFSM(user_id)
                print(user_id)
            await message.reply("Введите ваш уникальный логин:")

        @self.app.on_message(filters.regex("Регистрация"))
        async def handle_registration(client: Client, message: Message) -> None:
            """Обработчик кнопки регистрация"""
            user_id = message.from_user.id
            existing_user = await self.db.fetch_query(
                "SELECT * FROM users WHERE user_id = $1", user_id
            )
            if not existing_user:
                if user_id not in user_fsm:
                    user_fsm[user_id] = UserFSM(user_id)
                user_fsm[user_id].REGISTER()
                await register_command(client, message)
            else:
                await message.reply("С возвращением!", reply_markup=get_inline_menu())

        @self.app.on_message(filters.private)
        async def handle_message(client: Client, message: Message) -> None:
            """Обработчик сообщений"""
            user_id = message.from_user.id
            if user_id in user_fsm:
                state = user_fsm[user_id].state
                if state == "USERNAME":
                    await self.process_username_step(client, message)
                elif state == "PASSWORD":
                    await self.process_password_step(client, message)
            if user_id in task_fsm:
                state = task_fsm[user_id].state
                if state == "get_title":
                    await self.process_task_title_step(client, message)
                elif state == "get_description":
                    await self.process_task_description_step(client, message)

    async def process_username_step(self, client: Client, message: Message) -> None:
        """Ввод и проверка логина от пользователя"""
        user_id = message.from_user.id
        username = message.text
        existing_user = await self.db.fetch_query(
            "SELECT * FROM users WHERE username = $1", username
        )
        if existing_user:
            await message.reply("Этот логин уже занят. Введите другой.")
        else:
            await message.reply("Введите пароль (должен быть длиннее 8 символов):")
            user_fsm[user_id].username = username
            user_fsm[user_id].USERNAME()

    async def process_password_step(self, client: Client, message: Message) -> None:
        """Ввод и проверка пароля от пользователя"""
        user_id = message.from_user.id
        password = message.text

        # Проверяем пароль и получаем результат проверки
        password_error = check_password(password)
        if password_error:
            await message.reply(password_error)
            return

        username = user_fsm[user_id].username
        # Хэшируем пароль
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        await self.db.execute_query(
            "INSERT INTO users (user_id, username, password) VALUES ($1, $2, $3)",
            user_id,
            username,
            hashed_password.decode('utf-8'),
        )
        await message.reply(
            f"Пользователь {username} успешно зарегистрирован!",
            reply_markup=get_inline_menu(),
        )
        user_fsm[user_id].show_menu()

    async def process_task_title_step(self, client: Client, message: Message) -> None:
        """Ввод названия новой задачи"""
        user_id = message.from_user.id
        task_fsm[user_id].title = message.text
        task_fsm[user_id].set_title()
        await message.reply("Введите описание задачи:")

    async def process_task_description_step(
        self, client: Client, message: Message
    ) -> None:
        """Ввод описания новой задачи"""
        user_id = message.from_user.id
        task_fsm[user_id].description = message.text
        await self.db.execute_query(
            "INSERT INTO tasks (user_id, title, description) VALUES ($1, $2, $3)",
            user_id,
            task_fsm[user_id].title,
            task_fsm[user_id].description,
        )
        await message.reply("Задача успешно создана!", reply_markup=get_inline_menu())
        task_fsm[user_id].set_description()
