import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, BotCommand, CallbackQuery
from aiogram.filters import Command
from config import TOKEN
from database import init_db, toggle_task_completion, add_task
from handlers import start, add, show_tasks, show_archive, help_command, toggle_task, clear_archive, add_task_from_text

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Регистрируем обработчики
dp.message.register(start, Command("start"))
dp.message.register(add, Command("add"))
dp.message.register(show_tasks, Command("tasks"))
dp.message.register(show_archive, Command("archive"))
dp.message.register(help_command, Command("help"))
dp.message.register(add_task_from_text)
dp.callback_query.register(toggle_task, lambda c: c.data.startswith("task_"))
dp.callback_query.register(show_archive, lambda c: c.data == "view_archive")
dp.callback_query.register(clear_archive, lambda c: c.data == "clear_archive")


@dp.callback_query(lambda callback: callback.data.startswith("done_"))
async def complete_task(callback: types.CallbackQuery):
    task_id = int(callback.data.split("_")[1])

    # Обновляем статус задачи и получаем новый статус
    new_status = bool(toggle_task_completion(task_id))

    # Формируем новый текст кнопки
    updated_text = callback.message.text
    if new_status:
        updated_text += " ✅"
    else:
        updated_text = updated_text.replace(" ✅", "")

    # Обновляем текст сообщения с кнопкой
    await callback.message.edit_text(
        updated_text,
        reply_markup=callback.message.reply_markup
    )

    await callback.answer()


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
