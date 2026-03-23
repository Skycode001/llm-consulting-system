from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def get_main_keyboard() -> ReplyKeyboardMarkup:
    """
    Основная клавиатура с командами
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="/start"),
                KeyboardButton(text="/help"),
            ],
            [
                KeyboardButton(text="/status"),
                KeyboardButton(text="/token"),
            ],
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )


def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    """
    Клавиатура с кнопкой отмены
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="❌ Отмена")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )