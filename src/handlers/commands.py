"""
Обработчики команд бота
"""

from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from src.database.crud import (
    get_or_create_user,
    update_user_city,
    get_discounts_by_category,
    get_best_discounts
)
from src.handlers.keyboards import (
    get_main_menu_keyboard,
    get_city_keyboard,
    get_category_keyboard
)

router = Router()


class UserStates(StatesGroup):
    """Состояния пользователя"""
    selecting_city = State()
    selecting_category = State()
    browsing_discounts = State()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Обработчик команды /start"""
    user = await get_or_create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name
    )
    
    welcome_text = (
        f"👋 Привет, {message.from_user.first_name}!\n\n"
        "🛒 Я бот для отслеживания скидок в магазинах Беларуси.\n\n"
        "📍 <b>Доступные города:</b> Минск, Борисов, Жодино\n\n"
        "📦 <b>Категории магазинов:</b>\n"
        "• 🍎 Продукты\n"
        "• 👕 Одежда\n"
        "• 📱 Техника\n"
        "• 🏠 Товары для дома\n\n"
        "Выберите действие:"
    )
    
    await message.answer(welcome_text, reply_markup=get_main_menu_keyboard())


@router.message(Command("city"))
async def cmd_city(message: Message, state: FSMContext):
    """Обработчик команды /city - выбор города"""
    await state.set_state(UserStates.selecting_city)
    await message.answer(
        "🏙 Выберите ваш город:",
        reply_markup=get_city_keyboard()
    )


@router.message(Command("categories"))
async def cmd_categories(message: Message, state: FSMContext):
    """Обработчик команды /categories - выбор категории"""
    await state.set_state(UserStates.selecting_category)
    await message.answer(
        "📦 Выберите категорию магазинов:",
        reply_markup=get_category_keyboard()
    )


@router.message(Command("best"))
async def cmd_best_discounts(message: Message, state: FSMContext):
    """Обработчик команды /best - лучшие скидки"""
    user = await get_or_create_user(telegram_id=message.from_user.id)
    
    if not user.city:
        await message.answer(
            "⚠️ Сначала выберите город с помощью команды /city"
        )
        return
    
    discounts = await get_best_discounts(city=user.city, limit=10)
    
    if not discounts:
        await message.answer("😔 Пока нет доступных скидок в вашем городе.")
        return
    
    text = f"🔥 <b>Лучшие скидки в городе {user.city}:</b>\n\n"
    
    for i, discount in enumerate(discounts, 1):
        text += (
            f"{i}. <b>{discount.title}</b>\n"
            f"   🏪 {discount.store.name}\n"
            f"   💰 Скидка: {discount.discount_percent}%\n"
            f"   💵 Цена: {discount.new_price} BYN"
            f" (было {discount.old_price} BYN)\n"
            f"   📅 До: {discount.valid_until.strftime('%d.%m.%Y')}\n\n"
        )
    
    await message.answer(text)


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Обработчик команды /help"""
    help_text = (
        "📚 <b>Команды бота:</b>\n\n"
        "/start - Начать работу с ботом\n"
        "/city - Выбрать город\n"
        "/categories - Выбрать категорию магазинов\n"
        "/best - Показать лучшие скидки\n"
        "/subscriptions - Управление подписками\n"
        "/help - Показать эту справку\n\n"
        "💡 <b>Как пользоваться:</b>\n"
        "1. Выберите ваш город\n"
        "2. Выберите интересующую категорию\n"
        "3. Просматривайте актуальные скидки\n"
        "4. Подпишитесь на уведомления о новых скидках"
    )
    await message.answer(help_text)


@router.message(Command("subscriptions"))
async def cmd_subscriptions(message: Message):
    """Обработчик команды /subscriptions - управление подписками"""
    await message.answer(
        "🔔 <b>Управление подписками:</b>\n\n"
        "Здесь вы можете настроить уведомления о новых скидках.\n"
        "Выберите категории, о которых хотите получать уведомления:",
        reply_markup=get_category_keyboard(for_subscription=True)
    )
