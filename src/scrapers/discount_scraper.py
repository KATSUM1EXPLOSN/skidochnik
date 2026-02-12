"""
Главный модуль скрапинга скидок
"""

import logging
from typing import List, Dict, Any
from datetime import datetime

from src.scrapers.grocery import EvrooptScraper, GreenScraper
from src.scrapers.electronics import A21VekScraper
from src.scrapers.clothing import MileScraper
from src.database.crud import save_discount, get_store_by_name, create_store

logger = logging.getLogger(__name__)


class DiscountScraper:
    """Главный класс для сбора скидок со всех источников"""
    
    def __init__(self):
        # Инициализация всех скраперов
        self.scrapers = [
            # Продуктовые магазины
            EvrooptScraper(),
            GreenScraper(),
            # Техника
            A21VekScraper(),
            # Одежда
            MileScraper(),
        ]
        
    async def update_all_discounts(self) -> int:
        """
        Обновление скидок со всех источников
        
        Returns:
            int: Количество сохраненных скидок
        """
        total_saved = 0
        
        for scraper in self.scrapers:
            try:
                logger.info(f"Получение скидок от {scraper.store_name}...")
                discounts = await scraper.scrape_discounts()
                
                for discount_data in discounts:
                    try:
                        # Получаем или создаем магазин
                        store = await get_store_by_name(discount_data['store_name'])
                        if not store:
                            store = await create_store(
                                name=discount_data['store_name'],
                                category=discount_data['category'],
                                website=scraper.base_url
                            )
                        
                        # Сохраняем скидку
                        await save_discount(
                            store_id=store.id,
                            title=discount_data['title'],
                            old_price=discount_data['old_price'],
                            new_price=discount_data['new_price'],
                            discount_percent=discount_data['discount_percent'],
                            image_url=discount_data.get('image_url'),
                            product_url=discount_data.get('product_url'),
                            valid_until=discount_data.get('valid_until'),
                            city=discount_data.get('city', 'Минск')
                        )
                        total_saved += 1
                        
                    except Exception as e:
                        logger.error(f"Ошибка сохранения скидки: {e}")
                        continue
                        
                logger.info(f"Получено {len(discounts)} скидок от {scraper.store_name}")
                
            except Exception as e:
                logger.error(f"Ошибка при получении скидок от {scraper.store_name}: {e}")
                continue
        
        logger.info(f"Всего сохранено скидок: {total_saved}")
        return total_saved
    
    async def get_discounts_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Получение скидок по категории"""
        all_discounts = []
        
        for scraper in self.scrapers:
            if scraper.category == category:
                try:
                    discounts = await scraper.scrape_discounts()
                    all_discounts.extend(discounts)
                except Exception as e:
                    logger.error(f"Ошибка скрапинга {scraper.store_name}: {e}")
                    
        # Сортировка по проценту скидки (лучшие первыми)
        all_discounts.sort(key=lambda x: x.get('discount_percent', 0), reverse=True)
        
        return all_discounts
