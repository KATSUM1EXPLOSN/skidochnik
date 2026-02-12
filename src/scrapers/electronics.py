"""
Скраперы для магазинов электроники Беларуси
"""

import re
import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta

from src.scrapers.base import BaseScraper

logger = logging.getLogger(__name__)


class A21VekScraper(BaseScraper):
    """Скрапер для магазина 21vek.by"""
    
    def __init__(self):
        super().__init__(
            base_url="https://www.21vek.by",
            store_name="21vek",
            category="electronics"
        )
        
    async def scrape_discounts(self) -> List[Dict[str, Any]]:
        """Получение скидок с сайта 21vek"""
        discounts = []
        
        # Страница с акциями
        url = f"{self.base_url}/special_offers/discounts.html"
        html = await self.fetch_page(url)
        
        if not html:
            logger.warning("Не удалось загрузить страницу 21vek")
            return discounts
            
        soup = self.parse_html(html)
        
        # Поиск карточек товаров
        product_cards = soup.select('.g-item, .product-card, [data-product]')
        
        for card in product_cards:
            try:
                title_elem = card.select_one('.result__name, .product-title, .g-item-title')
                old_price_elem = card.select_one('.g-old-price, .price-old, .cost-old')
                new_price_elem = card.select_one('.g-price, .price-current, .cost-new')
                image_elem = card.select_one('img')
                link_elem = card.select_one('a.result__link, a.product-link')
                
                if not title_elem or not new_price_elem:
                    continue
                    
                title = title_elem.get_text(strip=True)
                new_price = self._parse_price(new_price_elem.get_text())
                old_price = self._parse_price(old_price_elem.get_text()) if old_price_elem else new_price
                
                if new_price <= 0:
                    continue
                
                discount = {
                    'title': title[:100],  # Ограничиваем длину
                    'old_price': old_price,
                    'new_price': new_price,
                    'discount_percent': self.calculate_discount_percent(old_price, new_price),
                    'image_url': image_elem.get('src') if image_elem else None,
                    'product_url': self.base_url + link_elem.get('href') if link_elem else None,
                    'valid_until': datetime.now() + timedelta(days=14),
                    'city': 'Минск',  # 21vek доставляет по всей Беларуси
                    'store_name': self.store_name,
                    'category': self.category
                }
                discounts.append(discount)
                
            except Exception as e:
                logger.debug(f"Ошибка парсинга карточки 21vek: {e}")
                continue
                
        return discounts
    
    def _parse_price(self, price_text: str) -> float:
        """Парсинг цены из текста"""
        try:
            # Удаляем все кроме цифр и разделителей
            price_str = re.sub(r'[^\d.,]', '', price_text)
            # Убираем пробелы между цифрами (1 234.56 -> 1234.56)
            price_str = price_str.replace(' ', '')
            price_str = price_str.replace(',', '.')
            return float(price_str) if price_str else 0
        except:
            return 0


class OnlinerScraper(BaseScraper):
    """Скрапер для каталога Onliner.by"""
    
    def __init__(self):
        super().__init__(
            base_url="https://catalog.onliner.by",
            store_name="Onliner",
            category="electronics"
        )
        
    async def scrape_discounts(self) -> List[Dict[str, Any]]:
        """Получение скидок с Onliner (через API)"""
        discounts = []
        
        # Onliner использует API для данных
        # Это placeholder - реальная реализация потребует работы с их API
        
        return discounts
