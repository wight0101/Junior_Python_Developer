import asyncio
import pandas as pd
import sqlite3
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.types import FSInputFile
from aiogram.filters import Command

TOKEN = 'YOUR-TOKEN'  # Замініть на токен з ботфазера

bot = Bot(token=TOKEN)
dp = Dispatcher()


DATABASE_URL = "jobs_history.db"

conn = sqlite3.connect(DATABASE_URL)
cursor = conn.cursor()

@dp.message(Command("get_today_statistic"))
async def send_today_statistic(message: types.Message):
    # Отримуємо записи з бази даних за поточну дату
    today = datetime.now().date().strftime('%Y-%m-%d')
    cursor.execute("SELECT query_time, job_count, change FROM job_queries WHERE DATE(query_time) = ?", (today,))
    queries = cursor.fetchall()

    if not queries:
        await message.answer("Сьогодні немає даних.")
        return

    # Формуємо DataFrame для експорту в Excel
    data = {
        'datetime': [datetime.strptime(query[0], '%Y-%m-%d %H:%M:%S.%f').strftime('%d.%m.%Y %H:%M:%S.%f')[:-3] for query in queries],
        'vacancy_count': [query[1] for query in queries],
        'change': [query[2] for query in queries]
    }

    df = pd.DataFrame(data)

    # Зберігаємо DataFrame в Excel
    file_path = 'zvitu\\today_statistic.xlsx'
    df.to_excel(file_path, index=False)

    # Надсилаємо файл користувачу
    file_to_send = FSInputFile(file_path)
    await message.answer_document(file_to_send)

async def bot_runner():
    await bot.delete_webhook(True)
    await dp.start_polling(bot)
