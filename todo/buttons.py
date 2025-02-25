from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def generate_task_buttons(tasks):
    if not tasks:
        return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Нет задач", callback_data="none")]])

    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=f"{task[1]} ✅" if task[2] else f"{task[1]}",  # Добавляем галочку, если выполнена
            callback_data=f"done_{task[0]}"
        )] for task in tasks
    ])
    return markup
