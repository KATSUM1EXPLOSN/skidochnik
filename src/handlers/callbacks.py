"""
Обработчики callback-запросов (нажатия на inline-кнопки)
"""

from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from src.database.crud import (
    get_or_create_user,
    update_user_city,
    get_discounts_by_category,
    toggle_subscription,
    get_stores_by_category
)
from src.handlers.keyboards import (
    get_main_menu_keyboard,
    get_category_keyboard,
    get_discounts_keyboard,
    get_back_keyboard,
    get_city_keyboard
)
from src.handlers.commands import UserStates

router = Router()


# Города Беларуси (областные центры и крупные города)
CITIES = {
    # Областные центры
    "minsk": "Минск",
    "brest": "Брест",
    "vitebsk": "Витебск",
    "gomel": "Гомель",
    "grodno": "Гродно",
    "mogilev": "Могилёв",
    # Крупные города
    "bobruisk": "Бобруйск",
    "baranovichi": "Барановичи",
    "borisov": "Борисов",
    "pinsk": "Пинск",
    "orsha": "Орша",
    "mozyr": "Мозырь",
    "soligorsk": "Солигорск",
    "novopolotsk": "Новополоцк",
    "lida": "Лида",
    "molodechno": "Молодечно",
    "polotsk": "Полоцк",
    "zhlobin": "Жлобин",
    "svetlogorsk": "Светлогорск",
    "rechitsa": "Речица",
    "slutsk": "Слуцк",
    "zhodino": "Жодино",
    "kobrin": "Кобрин",
    "slonim": "Слоним",
    "volkovysk": "Волковыск",
    "kalinkovichi": "Калинковичи",
    "smorgon": "Сморгонь",
    "rogachev": "Рогачёв",
    "osipovichi": "Осиповичи",
    "gorki": "Горки",
    "novogrudok": "Новогрудок",
    "bereza": "Берёза",
    "marina_gorka": "Марьина Горка",
    "vileika": "Вилейка",
    "mosty": "Мосты",
    "dzerzhinsk": "Дзержинск",
    "luninets": "Лунинец",
    "stolbtsy": "Столбцы",
    "glubokoe": "Глубокое",
    "nesvizh": "Несвиж",
}

# Категории
CATEGORIES = {
    "grocery": ("🍎 Продукты", "grocery"),
    "clothing": ("👕 Одежда", "clothing"),
    "electronics": ("📱 Техника", "electronics"),
    "home": ("🏠 Товары для дома", "home")
}


@router.callback_query(F.data.startswith("city:"))
async def process_city_selection(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора города"""
    city_code = callback.data.split(":")[1]
    city_name = CITIES.get(city_code)
    
    if not city_name:
        await callback.answer("Неизвестный город", show_alert=True)
        return
    
    await update_user_city(
        telegram_id=callback.from_user.id,
        city=city_name
    )
    
    await callback.message.edit_text(
        f"✅ Город <b>{city_name}</b> выбран!\n\n"
        "Теперь вы можете просматривать скидки в вашем городе.\n"
        "Используйте /categories для выбора категории или /best для лучших скидок.",
        reply_markup=get_main_menu_keyboard()
    )
    await state.clear()
    await callback.answer()


@router.callback_query(F.data.startswith("category:"))
async def process_category_selection(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора категории"""
    category_code = callback.data.split(":")[1]
    
    if category_code not in CATEGORIES:
        await callback.answer("Неизвестная категория", show_alert=True)
        return
    
    category_name, category_key = CATEGORIES[category_code]
    
    user = await get_or_create_user(telegram_id=callback.from_user.id)
    
    if not user.city:
        await callback.message.edit_text(
            "⚠️ Сначала выберите город с помощью команды /city"
        )
        await callback.answer()
        return
    
    discounts = await get_discounts_by_category(
        city=user.city,
        category=category_key,
        limit=10
    )
    
    if not discounts:
        await callback.message.edit_text(
            f"😔 Пока нет скидок в категории {category_name} в городе {user.city}.\n\n"
            "Попробуйте другую категорию или зайдите позже.",
            reply_markup=get_back_keyboard()
        )
        await callback.answer()
        return
    
    text = f"🏷 <b>Скидки в категории {category_name}</b>\n"
    text += f"📍 Город: {user.city}\n\n"
    
    for i, discount in enumerate(discounts, 1):
        text += (
            f"{i}. <b>{discount.title}</b>\n"
            f"   🏪 {discount.store.name}\n"
            f"   💰 -{discount.discount_percent}%\n"
            f"   💵 {discount.new_price} BYN (было {discount.old_price} BYN)\n\n"
        )
    
    await callback.message.edit_text(
        text,
        reply_markup=get_discounts_keyboard(category_key)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("subscribe:"))
async def process_subscription(callback: CallbackQuery):
    """Обработка подписки на категорию"""
    category_code = callback.data.split(":")[1]
    
    result = await toggle_subscription(
        telegram_id=callback.from_user.id,
        category=category_code
    )
    
    category_name = CATEGORIES.get(category_code, ("Категория",))[0]
    
    if result:
        await callback.answer(f"✅ Вы подписались на {category_name}", show_alert=True)
    else:
        await callback.answer(f"❌ Вы отписались от {category_name}", show_alert=True)


@router.callback_query(F.data == "back_to_menu")
async def process_back_to_menu(callback: CallbackQuery, state: FSMContext):
    """Возврат в главное меню"""
    await state.clear()
    await callback.message.edit_text(
        "📋 <b>Главное меню</b>\n\nВыберите действие:",
        reply_markup=get_main_menu_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "back_to_categories")
async def process_back_to_categories(callback: CallbackQuery):
    """Возврат к категориям"""
    await callback.message.edit_text(
        "📦 Выберите категорию магазинов:",
        reply_markup=get_category_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("cities_page:"))
async def process_cities_pagination(callback: CallbackQuery):
    """Пагинация списка городов"""
    page = int(callback.data.split(":")[1])
    await callback.message.edit_text(
        "🏙 Выберите ваш город:",
        reply_markup=get_city_keyboard(page=page)
    )
    await callback.answer()


@router.callback_query(F.data == "select_city")
async def process_select_city(callback: CallbackQuery, state: FSMContext):
    """Открытие выбора города"""
    await state.set_state(UserStates.selecting_city)
    await callback.message.edit_text(
        "🏙 Выберите ваш город:",
        reply_markup=get_city_keyboard(page=0)
    )
    await callback.answer()


@router.callback_query(F.data == "noop")
async def process_noop(callback: CallbackQuery):
    """Пустой обработчик для информационных кнопок"""
    await callback.answer()


@router.callback_query(F.data == "refresh_discounts")
async def process_refresh_discounts(callback: CallbackQuery):
    """Обновление списка скидок"""
    await callback.answer("🔄 Обновление данных...", show_alert=False)
    # Перезагружаем текущую категорию
    # Логика определения текущей категории через состояние
