import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
from config import TOKEN
from database import init_db
from handlers import register_handlers

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Регистрируем обработчики
register_handlers(dp)


async def set_bot_commands(bot):
    commands = [
        BotCommand(command="start", description="Начать работу с ботом"),
        BotCommand(command="add", description="Добавить задачу"),
        BotCommand(command="tasks", description="Показать текущие задачи"),
        BotCommand(command="help", description="Показать список команд"),
        BotCommand(command="archive", description="Показать архив задач"),
    ]
    await bot.set_my_commands(commands)


async def main():
    init_db()
    await bot.delete_webhook(drop_pending_updates=True)
    await set_bot_commands(bot)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())