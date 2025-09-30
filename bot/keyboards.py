from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_keyboard():
    buttons = [
        [KeyboardButton(text="💸 Добавить расход"), KeyboardButton(text="💵 Добавить доход")],
        [KeyboardButton(text="📊 Статистика"), KeyboardButton(text="💼 Баланс")],
        [KeyboardButton(text="📈 Дашборд")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def get_category_keyboard():
    buttons = [
        [KeyboardButton(text="🍔 Еда"), KeyboardButton(text="🚗 Транспорт")],
        [KeyboardButton(text="🏠 Жилье"), KeyboardButton(text="🎬 Развлечения")],
        [KeyboardButton(text="👕 Одежда"), KeyboardButton(text="💊 Здоровье")],
        [KeyboardButton(text="📚 Образование"), KeyboardButton(text="🎁 Подарки")],
        [KeyboardButton(text="💰 Другое"), KeyboardButton(text="❌ Отмена")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def get_income_source_keyboard():
    buttons = [
        [KeyboardButton(text="💼 Зарплата"), KeyboardButton(text="💰 Фриланс")],
        [KeyboardButton(text="🎁 Подарок"), KeyboardButton(text="📈 Инвестиции")],
        [KeyboardButton(text="💸 Другое"), KeyboardButton(text="❌ Отмена")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def get_skip_keyboard():
    buttons = [
        [KeyboardButton(text="⏭ Пропустить"), KeyboardButton(text="❌ Отмена")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def get_cancel_keyboard():
    buttons = [[KeyboardButton(text="❌ Отмена")]]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
