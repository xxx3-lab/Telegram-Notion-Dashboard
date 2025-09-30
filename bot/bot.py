import asyncio
import logging
import os
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import aiohttp
from keyboards import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_URL = os.getenv("API_URL", "http://backend:8000")

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

class ExpenseStates(StatesGroup):
    waiting_for_amount = State()
    waiting_for_category = State()
    waiting_for_description = State()

class IncomeStates(StatesGroup):
    waiting_for_amount = State()
    waiting_for_source = State()

# Категории расходов с эмодзи
EXPENSE_CATEGORIES = {
    "🍔 Еда": "Еда",
    "🚗 Транспорт": "Транспорт",
    "🏠 Жилье": "Жилье",
    "🎬 Развлечения": "Развлечения",
    "👕 Одежда": "Одежда",
    "💊 Здоровье": "Здоровье",
    "📚 Образование": "Образование",
    "🎁 Подарки": "Подарки",
    "💰 Другое": "Другое"
}

@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        f"👋 Привет, {message.from_user.first_name}!\n\n"
        "Я помогу тебе отслеживать финансы 💰\n\n"
        "Доступные команды:\n"
        "💸 /expense - Добавить расход\n"
        "💵 /income - Добавить доход\n"
        "📊 /stats - Статистика\n"
        "💼 /balance - Баланс\n"
        "📈 /report - Открыть дашборд\n\n"
        "Или используй быстрые кнопки ниже! ⬇️",
        reply_markup=get_main_keyboard()
    )

@dp.message(Command("expense"))
@dp.message(F.text == "💸 Добавить расход")
async def cmd_expense(message: Message, state: FSMContext):
    await state.set_state(ExpenseStates.waiting_for_amount)
    await message.answer(
        "💰 Введи сумму расхода:\n"
        "Например: 500 или 1250.50",
        reply_markup=get_cancel_keyboard()
    )

@dp.message(ExpenseStates.waiting_for_amount)
async def process_expense_amount(message: Message, state: FSMContext):
    try:
        amount = float(message.text.replace(",", "."))
        if amount <= 0:
            raise ValueError
        
        await state.update_data(amount=amount)
        await state.set_state(ExpenseStates.waiting_for_category)
        await message.answer(
            f"✅ Сумма: {amount} руб.\n\n"
            "Выбери категорию:",
            reply_markup=get_category_keyboard()
        )
    except ValueError:
        await message.answer(
            "❌ Неверная сумма! Введи число больше 0\n"
            "Например: 500 или 1250.50"
        )

@dp.message(ExpenseStates.waiting_for_category)
async def process_expense_category(message: Message, state: FSMContext):
    category = EXPENSE_CATEGORIES.get(message.text, message.text)
    await state.update_data(category=category)
    await state.set_state(ExpenseStates.waiting_for_description)
    await message.answer(
        f"📝 Категория: {category}\n\n"
        "Добавь описание или нажми 'Пропустить':",
        reply_markup=get_skip_keyboard()
    )

@dp.message(ExpenseStates.waiting_for_description)
async def process_expense_description(message: Message, state: FSMContext):
    data = await state.get_data()
    description = None if message.text == "⏭ Пропустить" else message.text
    
    async with aiohttp.ClientSession() as session:
        payload = {
            "user_id": message.from_user.id,
            "amount": data['amount'],
            "category": data['category'],
            "description": description,
            "date": datetime.now().date().isoformat()
        }
        
        try:
            async with session.post(f"{API_URL}/expenses/", json=payload) as resp:
                if resp.status == 200:
                    await message.answer(
                        "✅ Расход успешно добавлен!\n\n"
                        f"💰 Сумма: {data['amount']} руб.\n"
                        f"📂 Категория: {data['category']}\n"
                        f"📝 Описание: {description or 'Нет'}",
                        reply_markup=get_main_keyboard()
                    )
                else:
                    await message.answer(
                        "❌ Ошибка при сохранении расхода",
                        reply_markup=get_main_keyboard()
                    )
        except Exception as e:
            logger.error(f"Error saving expense: {e}")
            await message.answer(
                "❌ Ошибка подключения к серверу",
                reply_markup=get_main_keyboard()
            )
    
    await state.clear()

@dp.message(Command("income"))
@dp.message(F.text == "💵 Добавить доход")
async def cmd_income(message: Message, state: FSMContext):
    await state.set_state(IncomeStates.waiting_for_amount)
    await message.answer(
        "💵 Введи сумму дохода:\n"
        "Например: 50000",
        reply_markup=get_cancel_keyboard()
    )

@dp.message(IncomeStates.waiting_for_amount)
async def process_income_amount(message: Message, state: FSMContext):
    try:
        amount = float(message.text.replace(",", "."))
        if amount <= 0:
            raise ValueError
        
        await state.update_data(amount=amount)
        await state.set_state(IncomeStates.waiting_for_source)
        await message.answer(
            f"✅ Сумма: {amount} руб.\n\n"
            "Выбери источник дохода:",
            reply_markup=get_income_source_keyboard()
        )
    except ValueError:
        await message.answer("❌ Неверная сумма! Введи число больше 0")

@dp.message(IncomeStates.waiting_for_source)
async def process_income_source(message: Message, state: FSMContext):
    data = await state.get_data()
    source = message.text
    
    async with aiohttp.ClientSession() as session:
        payload = {
            "user_id": message.from_user.id,
            "amount": data['amount'],
            "source": source,
            "date": datetime.now().date().isoformat()
        }
        
        try:
            async with session.post(f"{API_URL}/income/", json=payload) as resp:
                if resp.status == 200:
                    await message.answer(
                        "✅ Доход успешно добавлен!\n\n"
                        f"💵 Сумма: {data['amount']} руб.\n"
                        f"📂 Источник: {source}",
                        reply_markup=get_main_keyboard()
                    )
                else:
                    await message.answer(
                        "❌ Ошибка при сохранении дохода",
                        reply_markup=get_main_keyboard()
                    )
        except Exception as e:
            logger.error(f"Error saving income: {e}")
            await message.answer(
                "❌ Ошибка подключения к серверу",
                reply_markup=get_main_keyboard()
            )
    
    await state.clear()

@dp.message(Command("stats"))
@dp.message(F.text == "📊 Статистика")
async def cmd_stats(message: Message):
    user_id = message.from_user.id
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"{API_URL}/stats/summary/?user_id={user_id}") as resp:
                summary = await resp.json()
            
            async with session.get(f"{API_URL}/stats/by-category/?user_id={user_id}&days=30") as resp:
                by_category = await resp.json()
            
            stats_text = "📊 **Статистика расходов**\n\n"
            stats_text += f"📅 Сегодня: {summary['today']:.2f} руб.\n"
            stats_text += f"📅 За неделю: {summary['week']:.2f} руб.\n"
            stats_text += f"📅 За месяц: {summary['month']:.2f} руб.\n\n"
            
            if by_category:
                stats_text += "📂 **По категориям (30 дней):**\n"
                for cat in sorted(by_category, key=lambda x: x['total'], reverse=True)[:5]:
                    stats_text += f"• {cat['category']}: {cat['total']:.2f} руб.\n"
            
            await message.answer(stats_text, parse_mode="Markdown")
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            await message.answer("❌ Ошибка получения статистики")

@dp.message(Command("balance"))
@dp.message(F.text == "💼 Баланс")
async def cmd_balance(message: Message):
    user_id = message.from_user.id
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"{API_URL}/balance/?user_id={user_id}") as resp:
                balance_data = await resp.json()
            
            balance_text = "💼 **Баланс**\n\n"
            balance_text += f"💵 Доходы: {balance_data['income']:.2f} руб.\n"
            balance_text += f"💸 Расходы: {balance_data['expenses']:.2f} руб.\n"
            balance_text += f"{'💰' if balance_data['balance'] >= 0 else '⚠️'} Остаток: {balance_data['balance']:.2f} руб."
            
            await message.answer(balance_text, parse_mode="Markdown")
        except Exception as e:
            logger.error(f"Error getting balance: {e}")
            await message.answer("❌ Ошибка получения баланса")

@dp.message(Command("report"))
@dp.message(F.text == "📈 Дашборд")
async def cmd_report(message: Message):
    dashboard_url = os.getenv("DASHBOARD_URL", "http://localhost:8050")
    await message.answer(
        f"📊 Открой дашборд для детальной аналитики:\n\n"
        f"🔗 {dashboard_url}?user_id={message.from_user.id}\n\n"
        f"На дашборде ты увидишь:\n"
        f"• 📊 Графики расходов по категориям\n"
        f"• 📈 Динамику расходов по дням\n"
        f"• 🫧 Bubble chart распределения\n"
        f"• 📉 Тренды и прогнозы\n"
        f"• 🔄 И многое другое!"
    )

@dp.message(F.text == "❌ Отмена")
async def cancel_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "❌ Действие отменено",
        reply_markup=get_main_keyboard()
    )

async def main():
    logger.info("Starting bot...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
