import time
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import schedule
import asyncio

# Налаштування бази даних
DATABASE_URL = "sqlite:///jobs_history.db"

Base = declarative_base()

class JobQuery(Base):
    __tablename__ = 'job_queries'
    id = Column(Integer, primary_key=True)
    query_time = Column(DateTime, default=datetime.now())
    job_count = Column(Integer)
    change = Column(Integer, default=0)

# Створення таблиці
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

def get_job_count():
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)

    try:
       
        driver.get("https://robota.ua/ru/zapros/junior/ukraine")

        # Знаходимо елемент, що містить кількість вакансій за допомогою наданого XPath
        job_count_element = driver.find_element(By.XPATH, "/html/body/app-root/div/alliance-jobseeker-vacancies-root-page/div/alliance-jobseeker-desktop-vacancies-page/main/section/div/div/lib-desktop-top-info/div/div/div")

        
        job_count_text = job_count_element.text

        
        job_count = int(''.join(filter(str.isdigit, job_count_text)))

        # Отримуємо останній запис з бази даних
        last_query = session.query(JobQuery).order_by(JobQuery.query_time.desc()).first()

        
        change = job_count - last_query.job_count if last_query else 0

        # Зберігаємо результат у базу даних
        new_query = JobQuery(job_count=job_count, change=change)
        session.add(new_query)
        session.commit()

        print(f"Кількість актуальних вакансій: {job_count}, Зміна: {change}")

    except Exception as e:
        print(f"Виникла помилка: {e}")
        session.rollback()

    finally:
        driver.quit()

# Виконуємо парсер щогодини
get_job_count()
schedule.every().hour.do(get_job_count)

async def scheduler():
    while True:
        schedule.run_pending()
        await asyncio.sleep(1)
