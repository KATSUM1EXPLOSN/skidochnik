"""
Конфигурация приложения
"""

import os
from pathlib import Path
from dataclasses import dataclass
from dotenv import load_dotenv

# Загрузка переменных окружения из .env файла
load_dotenv()

# Базовая директория проекта
BASE_DIR = Path(__file__).resolve().parent.parent


@dataclass
class Settings:
    """Настройки приложения"""
    
    # Telegram Bot
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        f"sqlite+aiosqlite:///{BASE_DIR}/data/discount_bot.db"
    )
    
    # Debug mode
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Scraping settings
    SCRAPE_INTERVAL_HOURS: int = int(os.getenv("SCRAPE_INTERVAL_HOURS", "24"))
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "30"))
    
    # Cities
    SUPPORTED_CITIES: list = None
    
    # Categories
    SUPPORTED_CATEGORIES: list = None
    
    def __post_init__(self):
        # Областные центры и крупные города Беларуси
        self.SUPPORTED_CITIES = [
            # Областные центры
            "Минск", "Брест", "Витебск", "Гомель", "Гродно", "Могилёв",
            # Крупные города
            "Бобруйск", "Барановичи", "Борисов", "Пинск", "Орша", "Мозырь",
            "Солигорск", "Новополоцк", "Лида", "Молодечно", "Полоцк", "Жлобин",
            "Светлогорск", "Речица", "Слуцк", "Жодино", "Кобрин", "Слоним",
            "Волковыск", "Калинковичи", "Сморгонь", "Рогачёв", "Осиповичи",
            "Горки", "Новогрудок", "Берёза", "Марьина Горка", "Вилейка",
            "Мосты", "Дзержинск", "Лунинец", "Столбцы", "Глубокое", "Несвиж"
        ]
        self.SUPPORTED_CATEGORIES = ["grocery", "clothing", "electronics", "home"]
        
        if not self.BOT_TOKEN:
            raise ValueError("BOT_TOKEN environment variable is required")


# Создаем экземпляр настроек
settings = Settings()
