"""
Скраперы для магазинов одежды Беларуси
"""

import re
import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta

from src.scrapers.base import BaseScraper

logger = logging.getLogger(__name__)


class MileScraper(BaseScraper):
    """Скрапер для магазина Mile.by"""
    
    def __init__(self):
        super().__init__(
            base_url="https://mile.by",
            store_name="Mile",
            category="clothing"
        )
        
    async def scrape_discounts(self) -> List[Dict[str, Any]]:
        """Получение скидок с сайта Mile"""
        discounts = []
        
        # Страница распродажи
        url = f"{self.base_url}/sale/"
        html = await self.fetch_page(url)
        
        if not html:
            logger.warning("Не удалось загрузить страницу Mile")
            return discounts
            
        soup = self.parse_html(html)
        
        # Поиск карточек товаров
        product_cards = soup.select('.product-card, .catalog-item, .product-item')
        
        for card in product_cards:
            try:
                title_elem = card.select_one('.product-name, .item-title, h3')
                old_price_elem = card.select_one('.old-price, .price-old')
                new_price_elem = card.select_one('.new-price, .price-new, .current-price')
                image_elem = card.select_one('img')
                link_elem = card.select_one('a')
                
                if not title_elem or not new_price_elem:
                    continue
                    
                title = title_elem.get_text(strip=True)
                new_price = self._parse_price(new_price_elem.get_text())
                old_price = self._parse_price(old_price_elem.get_text()) if old_price_elem else new_price
                
                if new_price <= 0:
                    continue
                
                discount = {
                    'title': title,
                    'old_price': old_price,
                    'new_price': new_price,
                    'discount_percent': self.calculate_discount_percent(old_price, new_price),
                    'image_url': image_elem.get('src') if image_elem else None,
                    'product_url': self.base_url + link_elem.get('href') if link_elem else None,
                    'valid_until': datetime.now() + timedelta(days=30),
                    'city': 'Минск',
                    'store_name': self.store_name,
                    'category': self.category
                }
                discounts.append(discount)
                
            except Exception as e:
                logger.debug(f"Ошибка парсинга карточки Mile: {e}")
                continue
                
        return discounts
    
    def _parse_price(self, price_text: str) -> float:
        """Парсинг цены"""
        try:
            price_str = re.sub(r'[^\d.,]', '', price_text)
            price_str = price_str.replace(',', '.')
            return float(price_str) if price_str else 0
        except:
            return 0


class MarkFormelleScraper(BaseScraper):
    """Скрапер для Mark Formelle"""
    
    def __init__(self):
        super().__init__(
            base_url="https://markformelle.by",
            store_name="Mark Formelle",
            category="clothing"
        )
        
    async def scrape_discounts(self) -> List[Dict[str, Any]]:
        """Получение скидок с сайта Mark Formelle"""
        discounts = []
        
        url = f"{self.base_url}/sale/"
        html = await self.fetch_page(url)
        
        if not html:
            return discounts
            
        soup = self.parse_html(html)
        product_cards = soup.select('.product-card, .catalog-product')
        
        for card in product_cards:
            try:
                title_elem = card.select_one('.product-name, .title')
                price_elem = card.select_one('.price-new, .sale-price')
                old_price_elem = card.select_one('.price-old')
                
                if not title_elem or not price_elem:
                    continue
                    
                title = title_elem.get_text(strip=True)
                new_price = self._parse_price(price_elem.get_text())
                old_price = self._parse_price(old_price_elem.get_text()) if old_price_elem else new_price
                
                if new_price <= 0:
                    continue
                
                discount = {
                    'title': title,
                    'old_price': old_price,
                    'new_price': new_price,
                    'discount_percent': self.calculate_discount_percent(old_price, new_price),
                    'valid_until': datetime.now() + timedelta(days=30),
                    'city': 'Минск',
                    'store_name': self.store_name,
                    'category': self.category
                }
                discounts.append(discount)
                
            except Exception as e:
                logger.debug(f"Ошибка парсинга Mark Formelle: {e}")
                continue
                
        return discounts
    
    def _parse_price(self, price_text: str) -> float:
        try:
            price_str = re.sub(r'[^\d.,]', '', price_text)
            price_str = price_str.replace(',', '.')
            return float(price_str) if price_str else 0
        except:
            return 0
