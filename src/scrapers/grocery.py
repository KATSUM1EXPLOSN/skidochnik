"""
Скраперы для продуктовых магазинов Беларуси
"""

import re
import logging
from typing import List, Dict, Any, Set
from datetime import datetime, timedelta

from src.scrapers.base import BaseScraper

logger = logging.getLogger(__name__)

# География продуктовых магазинов
GROCERY_STORE_CITIES = {
    "Евроопт": "all",  # Вся Беларусь
    "Green": ["Минск", "Гомель", "Брест", "Гродно", "Могилёв", "Витебск"],
    "Виталюр": ["Минск", "Гомель", "Могилёв", "Бобруйск"],
    "Санта": ["Брест", "Пинск", "Кобрин", "Барановичи", "Берёза"],
    "Корона": ["Минск", "Гомель"],
    "Гиппо": ["Минск", "Гомель", "Брест", "Гродно", "Витебск"],
    "Соседи": "all",
    "Рублёвский": ["Минск", "Борисов", "Жодино", "Солигорск", "Слуцк"],
    "Алми": ["Минск", "Борисов", "Молодечно", "Жодино"],
    "Белмаркет": ["Минск"],
    "Mart Inn": ["Минск", "Гомель"],
}


class EvrooptScraper(BaseScraper):
    """Скрапер для магазина Евроопт"""
    
    def __init__(self):
        super().__init__(
            base_url="https://evroopt.by",
            store_name="Евроопт",
            category="grocery"
        )
        
    async def scrape_discounts(self) -> List[Dict[str, Any]]:
        """Получение скидок с сайта Евроопт"""
        discounts = []
        
        # URL страницы со скидками/акциями
        url = f"{self.base_url}/special/"
        html = await self.fetch_page(url)
        
        if not html:
            logger.warning("Не удалось загрузить страницу Евроопт")
            return discounts
            
        soup = self.parse_html(html)
        
        # Поиск карточек товаров со скидками
        # Примечание: селекторы могут потребовать обновления при изменении структуры сайта
        product_cards = soup.select('.product-card, .special-item, .action-item')
        
        for card in product_cards:
            try:
                title_elem = card.select_one('.product-title, .item-title, h3')
                old_price_elem = card.select_one('.old-price, .price-old')
                new_price_elem = card.select_one('.new-price, .price-new, .price-current')
                image_elem = card.select_one('img')
                link_elem = card.select_one('a')
                
                if not title_elem or not new_price_elem:
                    continue
                    
                title = title_elem.get_text(strip=True)
                
                # Парсинг цен
                new_price = self._parse_price(new_price_elem.get_text())
                old_price = self._parse_price(old_price_elem.get_text()) if old_price_elem else new_price
                
                if old_price <= 0 or new_price <= 0:
                    continue
                
                discount = {
                    'title': title,
                    'old_price': old_price,
                    'new_price': new_price,
                    'discount_percent': self.calculate_discount_percent(old_price, new_price),
                    'image_url': image_elem.get('src') if image_elem else None,
                    'product_url': self.base_url + link_elem.get('href') if link_elem else None,
                    'valid_until': datetime.now() + timedelta(days=7),  # Примерный срок
                    'city': 'Минск',  # Евроопт работает во всех городах
                    'store_name': self.store_name,
                    'category': self.category
                }
                discounts.append(discount)
                
            except Exception as e:
                logger.debug(f"Ошибка парсинга карточки Евроопт: {e}")
                continue
                
        return discounts
    
    def _parse_price(self, price_text: str) -> float:
        """Парсинг цены из текста"""
        try:
            # Убираем все кроме цифр и точки/запятой
            price_str = re.sub(r'[^\d.,]', '', price_text)
            price_str = price_str.replace(',', '.')
            return float(price_str) if price_str else 0
        except:
            return 0


class GreenScraper(BaseScraper):
    """Скрапер для магазина Green"""
    
    cities = GROCERY_STORE_CITIES["Green"]
    
    def __init__(self):
        super().__init__(
            base_url="https://green-market.by",
            store_name="Green",
            category="grocery"
        )
        
    async def scrape_discounts(self) -> List[Dict[str, Any]]:
        """Получение скидок с сайта Green"""
        discounts = []
        
        url = f"{self.base_url}/actions/"
        html = await self.fetch_page(url)
        
        if not html:
            logger.warning("Не удалось загрузить страницу Green")
            return discounts
            
        soup = self.parse_html(html)
        product_cards = soup.select('.product-card, .action-product')
        
        for card in product_cards:
            try:
                title_elem = card.select_one('.product-name, .title')
                price_elem = card.select_one('.price')
                old_price_elem = card.select_one('.old-price')
                
                if not title_elem or not price_elem:
                    continue
                    
                title = title_elem.get_text(strip=True)
                new_price = self._parse_price(price_elem.get_text())
                old_price = self._parse_price(old_price_elem.get_text()) if old_price_elem else new_price
                
                if new_price <= 0:
                    continue
                
                # Создаём скидку для каждого города где есть магазин
                for city in self.cities:
                    discount = {
                        'title': title,
                        'old_price': old_price,
                        'new_price': new_price,
                        'discount_percent': self.calculate_discount_percent(old_price, new_price),
                        'valid_until': datetime.now() + timedelta(days=7),
                        'city': city,
                        'store_name': self.store_name,
                        'category': self.category
                    }
                    discounts.append(discount)
                
            except Exception as e:
                logger.debug(f"Ошибка парсинга карточки Green: {e}")
                continue
                
        return discounts
    
    def _parse_price(self, price_text: str) -> float:
        try:
            price_str = re.sub(r'[^\d.,]', '', price_text)
            price_str = price_str.replace(',', '.')
            return float(price_str) if price_str else 0
        except:
            return 0


class VitalurScraper(BaseScraper):
    """Скрапер для магазина Виталюр"""
    
    cities = GROCERY_STORE_CITIES["Виталюр"]
    
    def __init__(self):
        super().__init__(
            base_url="https://vitalur.by",
            store_name="Виталюр",
            category="grocery"
        )
        
    async def scrape_discounts(self) -> List[Dict[str, Any]]:
        discounts = []
        url = f"{self.base_url}/actions/"
        html = await self.fetch_page(url)
        
        if not html:
            return discounts
            
        soup = self.parse_html(html)
        product_cards = soup.select('.product-card, .action-item, .promo-item')
        
        for card in product_cards:
            try:
                title_elem = card.select_one('.product-title, .name, h3')
                old_price_elem = card.select_one('.old-price, .price-old')
                new_price_elem = card.select_one('.new-price, .price-new, .price')
                
                if not title_elem or not new_price_elem:
                    continue
                    
                title = title_elem.get_text(strip=True)
                new_price = self._parse_price(new_price_elem.get_text())
                old_price = self._parse_price(old_price_elem.get_text()) if old_price_elem else new_price
                
                if new_price <= 0:
                    continue
                
                for city in self.cities:
                    discount = {
                        'title': title,
                        'old_price': old_price,
                        'new_price': new_price,
                        'discount_percent': self.calculate_discount_percent(old_price, new_price),
                        'valid_until': datetime.now() + timedelta(days=7),
                        'city': city,
                        'store_name': self.store_name,
                        'category': self.category
                    }
                    discounts.append(discount)
                
            except Exception as e:
                logger.debug(f"Ошибка парсинга Виталюр: {e}")
                continue
                
        return discounts
    
    def _parse_price(self, price_text: str) -> float:
        try:
            price_str = re.sub(r'[^\d.,]', '', price_text)
            price_str = price_str.replace(',', '.')
            return float(price_str) if price_str else 0
        except:
            return 0


class SantaScraper(BaseScraper):
    """Скрапер для магазина Санта (Брестская область)"""
    
    cities = GROCERY_STORE_CITIES["Санта"]
    
    def __init__(self):
        super().__init__(
            base_url="https://santa.by",
            store_name="Санта",
            category="grocery"
        )
        
    async def scrape_discounts(self) -> List[Dict[str, Any]]:
        discounts = []
        url = f"{self.base_url}/aktsii/"
        html = await self.fetch_page(url)
        
        if not html:
            return discounts
            
        soup = self.parse_html(html)
        product_cards = soup.select('.product-card, .action-item')
        
        for card in product_cards:
            try:
                title_elem = card.select_one('.product-title, .name')
                old_price_elem = card.select_one('.old-price')
                new_price_elem = card.select_one('.new-price, .price')
                
                if not title_elem or not new_price_elem:
                    continue
                    
                title = title_elem.get_text(strip=True)
                new_price = self._parse_price(new_price_elem.get_text())
                old_price = self._parse_price(old_price_elem.get_text()) if old_price_elem else new_price
                
                if new_price <= 0:
                    continue
                
                for city in self.cities:
                    discount = {
                        'title': title,
                        'old_price': old_price,
                        'new_price': new_price,
                        'discount_percent': self.calculate_discount_percent(old_price, new_price),
                        'valid_until': datetime.now() + timedelta(days=7),
                        'city': city,
                        'store_name': self.store_name,
                        'category': self.category
                    }
                    discounts.append(discount)
                
            except Exception as e:
                logger.debug(f"Ошибка парсинга Санта: {e}")
                continue
                
        return discounts
    
    def _parse_price(self, price_text: str) -> float:
        try:
            price_str = re.sub(r'[^\d.,]', '', price_text)
            price_str = price_str.replace(',', '.')
            return float(price_str) if price_str else 0
        except:
            return 0


class GippoScraper(BaseScraper):
    """Скрапер для гипермаркетов Гиппо"""
    
    cities = GROCERY_STORE_CITIES["Гиппо"]
    
    def __init__(self):
        super().__init__(
            base_url="https://gippo.by",
            store_name="Гиппо",
            category="grocery"
        )
        
    async def scrape_discounts(self) -> List[Dict[str, Any]]:
        discounts = []
        url = f"{self.base_url}/actions/"
        html = await self.fetch_page(url)
        
        if not html:
            return discounts
            
        soup = self.parse_html(html)
        product_cards = soup.select('.product-card, .action-item, .promo-product')
        
        for card in product_cards:
            try:
                title_elem = card.select_one('.product-title, .name, h3')
                old_price_elem = card.select_one('.old-price')
                new_price_elem = card.select_one('.new-price, .price')
                
                if not title_elem or not new_price_elem:
                    continue
                    
                title = title_elem.get_text(strip=True)
                new_price = self._parse_price(new_price_elem.get_text())
                old_price = self._parse_price(old_price_elem.get_text()) if old_price_elem else new_price
                
                if new_price <= 0:
                    continue
                
                for city in self.cities:
                    discount = {
                        'title': title,
                        'old_price': old_price,
                        'new_price': new_price,
                        'discount_percent': self.calculate_discount_percent(old_price, new_price),
                        'valid_until': datetime.now() + timedelta(days=7),
                        'city': city,
                        'store_name': self.store_name,
                        'category': self.category
                    }
                    discounts.append(discount)
                
            except Exception as e:
                logger.debug(f"Ошибка парсинга Гиппо: {e}")
                continue
                
        return discounts
    
    def _parse_price(self, price_text: str) -> float:
        try:
            price_str = re.sub(r'[^\d.,]', '', price_text)
            price_str = price_str.replace(',', '.')
            return float(price_str) if price_str else 0
        except:
            return 0


class SosediScraper(BaseScraper):
    """Скрапер для магазинов Соседи"""
    
    def __init__(self):
        super().__init__(
            base_url="https://sosedi.by",
            store_name="Соседи",
            category="grocery"
        )
        
    async def scrape_discounts(self) -> List[Dict[str, Any]]:
        discounts = []
        url = f"{self.base_url}/special/"
        html = await self.fetch_page(url)
        
        if not html:
            return discounts
            
        soup = self.parse_html(html)
        product_cards = soup.select('.product-card, .special-item')
        
        for card in product_cards:
            try:
                title_elem = card.select_one('.product-title, .name')
                old_price_elem = card.select_one('.old-price')
                new_price_elem = card.select_one('.new-price, .price')
                
                if not title_elem or not new_price_elem:
                    continue
                    
                title = title_elem.get_text(strip=True)
                new_price = self._parse_price(new_price_elem.get_text())
                old_price = self._parse_price(old_price_elem.get_text()) if old_price_elem else new_price
                
                if new_price <= 0:
                    continue
                
                # Соседи работают по всей Беларуси - используем 'all'
                discount = {
                    'title': title,
                    'old_price': old_price,
                    'new_price': new_price,
                    'discount_percent': self.calculate_discount_percent(old_price, new_price),
                    'valid_until': datetime.now() + timedelta(days=7),
                    'city': 'all',  # Все города
                    'store_name': self.store_name,
                    'category': self.category
                }
                discounts.append(discount)
                
            except Exception as e:
                logger.debug(f"Ошибка парсинга Соседи: {e}")
                continue
                
        return discounts
    
    def _parse_price(self, price_text: str) -> float:
        try:
            price_str = re.sub(r'[^\d.,]', '', price_text)
            price_str = price_str.replace(',', '.')
            return float(price_str) if price_str else 0
        except:
            return 0


class KoronaScraper(BaseScraper):
    """Скрапер для гипермаркетов Корона"""
    
    cities = GROCERY_STORE_CITIES["Корона"]
    
    def __init__(self):
        super().__init__(
            base_url="https://korona.by",
            store_name="Корона",
            category="grocery"
        )
        
    async def scrape_discounts(self) -> List[Dict[str, Any]]:
        discounts = []
        url = f"{self.base_url}/actions/"
        html = await self.fetch_page(url)
        
        if not html:
            return discounts
            
        soup = self.parse_html(html)
        product_cards = soup.select('.product-card, .action-item')
        
        for card in product_cards:
            try:
                title_elem = card.select_one('.product-title, .name')
                old_price_elem = card.select_one('.old-price')
                new_price_elem = card.select_one('.new-price, .price')
                
                if not title_elem or not new_price_elem:
                    continue
                    
                title = title_elem.get_text(strip=True)
                new_price = self._parse_price(new_price_elem.get_text())
                old_price = self._parse_price(old_price_elem.get_text()) if old_price_elem else new_price
                
                if new_price <= 0:
                    continue
                
                for city in self.cities:
                    discount = {
                        'title': title,
                        'old_price': old_price,
                        'new_price': new_price,
                        'discount_percent': self.calculate_discount_percent(old_price, new_price),
                        'valid_until': datetime.now() + timedelta(days=7),
                        'city': city,
                        'store_name': self.store_name,
                        'category': self.category
                    }
                    discounts.append(discount)
                
            except Exception as e:
                logger.debug(f"Ошибка парсинга Корона: {e}")
                continue
                
        return discounts
    
    def _parse_price(self, price_text: str) -> float:
        try:
            price_str = re.sub(r'[^\d.,]', '', price_text)
            price_str = price_str.replace(',', '.')
            return float(price_str) if price_str else 0
        except:
            return 0
