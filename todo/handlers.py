import sqlite3
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import Dispatcher
from database import add_task, get_tasks, get_archive, toggle_task_completion, clear_archive_db
from buttons import generate_task_buttons


def register_handlers(dp: Dispatcher):
    dp.callback_query.register(clear_archive, lambda c: c.data == "clear_archive")
    dp.register_message_handler(start, commands=["start"])
    dp.register_message_handler(add, commands=["add"])
    dp.register_message_handler(show_tasks, commands=["tasks"])
    dp.register_message_handler(show_archive, commands=["archive"])
    dp.register_message_handler(help_command, commands=["help"])
    dp.register_callback_query_handler(toggle_task, lambda c: c.data.startswith("task_"))


async def add_task_from_text(message: types.Message):
    """Добавляет задачу, если пользователь просто отправил текст без команды."""
    task_text = message.text.strip()

    # Проверяем, что это не команда (не начинается с "/")
    if not task_text.startswith("/"):
        add_task(task_text)
        await message.answer(f"✅ Задача добавлена: {task_text}")


async def start(message: types.Message):
    await message.answer("Привет! Это твой список дел. Добавь задачу с помощью /add <текст>.")


async def add(message: types.Message):
    task_text = message.text[5:].strip()
    if task_text:
        add_task(task_text)
        await message.answer(f"✅ Задача добавлена: {task_text}")
    else:
        await message.answer("❌ Напиши задачу после команды /add")


async def show_tasks(message: types.Message):
    tasks = get_tasks()
    if not tasks:
        await message.answer("У тебя пока нет задач.")
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    for task_id, description, completed in tasks:
        checkmark = " ✅" if completed else ""
        button = InlineKeyboardButton(text=f"\u200B{description}{checkmark}", callback_data=f"task_{task_id}")
        keyboard.inline_keyboard.append([button])

    await message.answer("📌 Твои задачи:", reply_markup=keyboard)


async def toggle_task(callback_query: types.CallbackQuery):
    task_id = int(callback_query.data.split("_")[1])
    toggle_task_completion(task_id)  # Меняем статус в БД

    # Получаем обновленный список задач
    tasks = get_tasks()

    if not tasks:
        await callback_query.message.edit_text("📭 Все задачи выполнены и перемещены в архив.")
        return

    # Перерисовываем клавиатуру с обновленным списком задач
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=f"\u200B{task[1]} ✅" if task[2] else f"\u200B{task[1]}",
            callback_data=f"task_{task[0]}"
        )] for task in tasks
    ])

    await callback_query.message.edit_text("📌 Твои задачи:", reply_markup=keyboard)
    await callback_query.answer("Задача обновлена!")


async def show_archive(message: types.Message):
    archive = get_archive()
    if archive:
        archive_text = "\n".join([task[0] for task in archive])
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🗑 Очистить архив", callback_data="clear_archive")]
        ])
        await message.answer(f"📜 Архив:\n{archive_text}", reply_markup=keyboard)
    else:
        await message.answer("📭 Архив пуст.")


async def clear_archive(callback_query: types.CallbackQuery):
    clear_archive_db()
    await callback_query.message.edit_text("📭 Архив очищен.")
    await callback_query.answer("Архив удалён!")


async def help_command(message: types.Message):
    text = (
        "Доступные команды:\n"
        "/start - Начать работу с ботом\n"
        "/add - Добавить задачу\n"
        "/tasks - Показать текущие задачи\n"
        "/archive - Показать архив задач\n"
        "/help - Показать список команд"
    )
    await message.answer(text)
