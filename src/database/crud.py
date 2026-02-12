"""
CRUD операции для базы данных
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import select, update, delete, and_, desc
from sqlalchemy.orm import selectinload

from src.database.models import (
    async_session,
    User,
    Store,
    Discount,
    Subscription
)


# ===================== USER OPERATIONS =====================

async def get_or_create_user(
    telegram_id: int,
    username: Optional[str] = None,
    first_name: Optional[str] = None
) -> User:
    """Получить или создать пользователя"""
    async with async_session() as session:
        # Попытка найти пользователя
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        
        if user:
            # Обновляем информацию, если изменилась
            if username and user.username != username:
                user.username = username
            if first_name and user.first_name != first_name:
                user.first_name = first_name
            await session.commit()
            return user
        
        # Создаем нового пользователя
        user = User(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


async def update_user_city(telegram_id: int, city: str) -> Optional[User]:
    """Обновить город пользователя"""
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        
        if user:
            user.city = city
            await session.commit()
            await session.refresh(user)
        
        return user


async def get_user_by_telegram_id(telegram_id: int) -> Optional[User]:
    """Получить пользователя по Telegram ID"""
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()


# ===================== STORE OPERATIONS =====================

async def get_store_by_name(name: str) -> Optional[Store]:
    """Получить магазин по имени"""
    async with async_session() as session:
        result = await session.execute(
            select(Store).where(Store.name == name)
        )
        return result.scalar_one_or_none()


async def create_store(
    name: str,
    category: str,
    website: Optional[str] = None,
    logo_url: Optional[str] = None,
    description: Optional[str] = None
) -> Store:
    """Создать новый магазин"""
    async with async_session() as session:
        store = Store(
            name=name,
            category=category,
            website=website,
            logo_url=logo_url,
            description=description
        )
        session.add(store)
        await session.commit()
        await session.refresh(store)
        return store


async def get_stores_by_category(category: str) -> List[Store]:
    """Получить магазины по категории"""
    async with async_session() as session:
        result = await session.execute(
            select(Store).where(Store.category == category)
        )
        return result.scalars().all()


# ===================== DISCOUNT OPERATIONS =====================

async def save_discount(
    store_id: int,
    title: str,
    new_price: float,
    old_price: Optional[float] = None,
    discount_percent: Optional[int] = None,
    image_url: Optional[str] = None,
    product_url: Optional[str] = None,
    valid_until: Optional[datetime] = None,
    city: str = "Минск"
) -> Discount:
    """Сохранить скидку"""
    async with async_session() as session:
        # Проверяем, существует ли уже такая скидка
        result = await session.execute(
            select(Discount).where(
                and_(
                    Discount.store_id == store_id,
                    Discount.title == title,
                    Discount.is_active == True
                )
            )
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            # Обновляем существующую скидку
            existing.old_price = old_price
            existing.new_price = new_price
            existing.discount_percent = discount_percent
            existing.valid_until = valid_until
            existing.updated_at = datetime.utcnow()
            await session.commit()
            await session.refresh(existing)
            return existing
        
        # Создаем новую скидку
        discount = Discount(
            store_id=store_id,
            title=title,
            old_price=old_price,
            new_price=new_price,
            discount_percent=discount_percent,
            image_url=image_url,
            product_url=product_url,
            valid_until=valid_until,
            city=city
        )
        session.add(discount)
        await session.commit()
        await session.refresh(discount)
        return discount


async def get_discounts_by_category(
    city: str,
    category: str,
    limit: int = 20
) -> List[Discount]:
    """Получить скидки по категории и городу"""
    async with async_session() as session:
        result = await session.execute(
            select(Discount)
            .join(Store)
            .where(
                and_(
                    Store.category == category,
                    Discount.city == city,
                    Discount.is_active == True
                )
            )
            .options(selectinload(Discount.store))
            .order_by(desc(Discount.discount_percent))
            .limit(limit)
        )
        return result.scalars().all()


async def get_best_discounts(city: str, limit: int = 10) -> List[Discount]:
    """Получить лучшие скидки по городу (сортировка по проценту скидки)"""
    async with async_session() as session:
        result = await session.execute(
            select(Discount)
            .where(
                and_(
                    Discount.city == city,
                    Discount.is_active == True,
                    Discount.discount_percent.isnot(None)
                )
            )
            .options(selectinload(Discount.store))
            .order_by(desc(Discount.discount_percent))
            .limit(limit)
        )
        return result.scalars().all()


async def deactivate_old_discounts():
    """Деактивировать устаревшие скидки"""
    async with async_session() as session:
        await session.execute(
            update(Discount)
            .where(
                and_(
                    Discount.valid_until < datetime.utcnow(),
                    Discount.is_active == True
                )
            )
            .values(is_active=False)
        )
        await session.commit()


# ===================== SUBSCRIPTION OPERATIONS =====================

async def toggle_subscription(telegram_id: int, category: str) -> bool:
    """Переключить подписку на категорию. Возвращает True если подписка активирована."""
    async with async_session() as session:
        # Получаем пользователя
        user_result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = user_result.scalar_one_or_none()
        
        if not user:
            return False
        
        # Проверяем существующую подписку
        sub_result = await session.execute(
            select(Subscription).where(
                and_(
                    Subscription.user_id == user.id,
                    Subscription.category == category
                )
            )
        )
        subscription = sub_result.scalar_one_or_none()
        
        if subscription:
            # Переключаем статус
            subscription.is_active = not subscription.is_active
            await session.commit()
            return subscription.is_active
        else:
            # Создаем новую подписку
            subscription = Subscription(
                user_id=user.id,
                category=category,
                is_active=True
            )
            session.add(subscription)
            await session.commit()
            return True


async def get_user_subscriptions(telegram_id: int) -> List[Subscription]:
    """Получить активные подписки пользователя"""
    async with async_session() as session:
        result = await session.execute(
            select(Subscription)
            .join(User)
            .where(
                and_(
                    User.telegram_id == telegram_id,
                    Subscription.is_active == True
                )
            )
        )
        return result.scalars().all()


async def get_subscribers_by_category(category: str) -> List[User]:
    """Получить всех подписчиков категории для рассылки"""
    async with async_session() as session:
        result = await session.execute(
            select(User)
            .join(Subscription)
            .where(
                and_(
                    Subscription.category == category,
                    Subscription.is_active == True,
                    User.is_active == True
                )
            )
        )
        return result.scalars().all()
