"""
Базовый класс скрапера
"""

import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import aiohttp
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """Базовый класс для всех скраперов"""
    
    def __init__(self, base_url: str, store_name: str, category: str):
        self.base_url = base_url
        self.store_name = store_name
        self.category = category
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        }
        
    async def fetch_page(self, url: str) -> Optional[str]:
        """Загрузка HTML страницы"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers, timeout=30) as response:
                    if response.status == 200:
                        return await response.text()
                    else:
                        logger.warning(f"Ошибка загрузки {url}: статус {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Ошибка при загрузке страницы {url}: {e}")
            return None
            
    def parse_html(self, html: str) -> BeautifulSoup:
        """Парсинг HTML"""
        return BeautifulSoup(html, 'html.parser')
    
    @abstractmethod
    async def scrape_discounts(self) -> List[Dict[str, Any]]:
        """
        Получение списка скидок
        
        Returns:
            List[Dict]: Список скидок в формате:
            [
                {
                    'title': 'Название товара',
                    'old_price': 10.99,
                    'new_price': 7.99,
                    'discount_percent': 27,
                    'image_url': 'https://...',
                    'product_url': 'https://...',
                    'valid_until': datetime,
                    'city': 'Минск',
                    'store_name': 'Евроопт',
                    'category': 'grocery'
                }
            ]
        """
        pass
    
    def calculate_discount_percent(self, old_price: float, new_price: float) -> int:
        """Расчет процента скидки"""
        if old_price <= 0:
            return 0
        discount = ((old_price - new_price) / old_price) * 100
        return int(round(discount))
