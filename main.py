"""
Telegram Discount Bot - Главный модуль запуска
Бот для отслеживания скидок в магазинах Беларуси
"""

import asyncio
import logging
from src.bot import DiscountBot
from config.settings import settings

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


async def main():
    """Главная функция запуска бота"""
    logger.info("Запуск Telegram Discount Bot...")
    
    bot = DiscountBot(token=settings.BOT_TOKEN)
    
    try:
        await bot.start()
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
        raise
    finally:
        await bot.stop()


if __name__ == "__main__":
    asyncio.run(main())
