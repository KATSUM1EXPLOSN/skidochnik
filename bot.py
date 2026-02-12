"""
Основной модуль бота
"""

import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from src.handlers.commands import router as commands_router
from src.handlers.callbacks import router as callbacks_router
from src.database.models import init_db
from src.scrapers import DiscountScraper

logger = logging.getLogger(__name__)


class DiscountBot:
    """Главный класс Telegram бота для отслеживания скидок"""
    
    def __init__(self, token: str):
        self.bot = Bot(
            token=token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        self.dp = Dispatcher()
        self.scheduler = AsyncIOScheduler()
        self.scraper = DiscountScraper()
        
        # Регистрация роутеров
        self.dp.include_router(commands_router)
        self.dp.include_router(callbacks_router)
        
    async def start(self):
        """Запуск бота"""
        logger.info("Инициализация базы данных...")
        await init_db()
        
        logger.info("Настройка планировщика задач...")
        self._setup_scheduler()
        self.scheduler.start()
        
        logger.info("Запуск polling...")
        await self.dp.start_polling(self.bot)
        
    async def stop(self):
        """Остановка бота"""
        logger.info("Остановка бота...")
        self.scheduler.shutdown()
        await self.bot.session.close()
        
    def _setup_scheduler(self):
        """Настройка планировщика для ежедневного обновления скидок"""
        # Обновление скидок каждый день в 6:00 утра
        self.scheduler.add_job(
            self._update_discounts,
            'cron',
            hour=6,
            minute=0,
            id='daily_discount_update'
        )
        
        # Также запускаем обновление при старте
        self.scheduler.add_job(
            self._update_discounts,
            'date',
            id='startup_discount_update'
        )
        
    async def _update_discounts(self):
        """Обновление информации о скидках"""
        logger.info("Начало обновления скидок...")
        try:
            await self.scraper.update_all_discounts()
            logger.info("Скидки успешно обновлены")
        except Exception as e:
            logger.error(f"Ошибка при обновлении скидок: {e}")
