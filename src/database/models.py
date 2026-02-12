"""
Модели базы данных SQLite
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, relationship
from config.settings import settings


class Base(DeclarativeBase):
    """Базовый класс для всех моделей"""
    pass


class User(Base):
    """Модель пользователя"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(Integer, unique=True, nullable=False, index=True)
    username = Column(String(100), nullable=True)
    first_name = Column(String(100), nullable=True)
    city = Column(String(50), nullable=True, default="Минск")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Отношения
    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")


class Store(Base):
    """Модель магазина"""
    __tablename__ = "stores"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False, unique=True)
    category = Column(String(50), nullable=False, index=True)  # grocery, clothing, electronics, home
    website = Column(String(500), nullable=True)
    logo_url = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    cities = Column(String(500), default="Минск,Борисов,Жодино")  # Города где работает магазин
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Отношения
    discounts = relationship("Discount", back_populates="store", cascade="all, delete-orphan")


class Discount(Base):
    """Модель скидки/акции"""
    __tablename__ = "discounts"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    old_price = Column(Float, nullable=True)
    new_price = Column(Float, nullable=False)
    discount_percent = Column(Integer, nullable=True)
    image_url = Column(String(1000), nullable=True)
    product_url = Column(String(1000), nullable=True)
    city = Column(String(50), default="Минск", index=True)
    valid_from = Column(DateTime, default=datetime.utcnow)
    valid_until = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Отношения
    store = relationship("Store", back_populates="discounts")


class Subscription(Base):
    """Модель подписки пользователя на категорию"""
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category = Column(String(50), nullable=False)  # grocery, clothing, electronics, home
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Отношения
    user = relationship("User", back_populates="subscriptions")


# Создание асинхронного движка
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG
)

# Создание фабрики сессий
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def init_db():
    """Инициализация базы данных"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncSession:
    """Получение сессии базы данных"""
    async with async_session() as session:
        yield session
