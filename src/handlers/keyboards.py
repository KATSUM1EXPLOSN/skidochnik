"""
Клавиатуры для бота
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Главное меню"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="🏙 Выбрать город", callback_data="select_city"),
        InlineKeyboardButton(text="📦 Категории", callback_data="select_categories")
    )
    builder.row(
        InlineKeyboardButton(text="🔥 Лучшие скидки", callback_data="best_discounts"),
        InlineKeyboardButton(text="🔔 Подписки", callback_data="subscriptions")
    )
    
    return builder.as_markup()


def get_city_keyboard(page: int = 0) -> InlineKeyboardMarkup:
    """Клавиатура выбора города с пагинацией"""
    builder = InlineKeyboardBuilder()
    
    # Все города сгруппированы
    all_cities = [
        # Областные центры (первые в списке)
        ("🏛 Минск", "city:minsk"),
        ("🏛 Брест", "city:brest"),
        ("🏛 Витебск", "city:vitebsk"),
        ("🏛 Гомель", "city:gomel"),
        ("🏛 Гродно", "city:grodno"),
        ("🏛 Могилёв", "city:mogilev"),
        # Крупные города
        ("🏙 Бобруйск", "city:bobruisk"),
        ("🏙 Барановичи", "city:baranovichi"),
        ("🏙 Борисов", "city:borisov"),
        ("🏙 Пинск", "city:pinsk"),
        ("🏙 Орша", "city:orsha"),
        ("🏙 Мозырь", "city:mozyr"),
        ("🏙 Солигорск", "city:soligorsk"),
        ("🏙 Новополоцк", "city:novopolotsk"),
        ("🏙 Лида", "city:lida"),
        ("🏙 Молодечно", "city:molodechno"),
        ("🏙 Полоцк", "city:polotsk"),
        ("🏙 Жлобин", "city:zhlobin"),
        ("🏙 Светлогорск", "city:svetlogorsk"),
        ("🏙 Речица", "city:rechitsa"),
        ("🏙 Слуцк", "city:slutsk"),
        ("🏙 Жодино", "city:zhodino"),
        ("🏙 Кобрин", "city:kobrin"),
        ("🏙 Слоним", "city:slonim"),
        ("🏙 Волковыск", "city:volkovysk"),
        ("🏙 Калинковичи", "city:kalinkovichi"),
        ("🏙 Сморгонь", "city:smorgon"),
        ("🏙 Рогачёв", "city:rogachev"),
        ("🏙 Осиповичи", "city:osipovichi"),
        ("🏙 Горки", "city:gorki"),
        ("🏙 Новогрудок", "city:novogrudok"),
        ("🏙 Берёза", "city:bereza"),
        ("🏙 Марьина Горка", "city:marina_gorka"),
        ("🏙 Вилейка", "city:vileika"),
        ("🏙 Мосты", "city:mosty"),
        ("🏙 Дзержинск", "city:dzerzhinsk"),
        ("🏙 Лунинец", "city:luninets"),
        ("🏙 Столбцы", "city:stolbtsy"),
        ("🏙 Глубокое", "city:glubokoe"),
        ("🏙 Несвиж", "city:nesvizh"),
    ]
    
    # Пагинация: 8 городов на страницу
    cities_per_page = 8
    total_pages = (len(all_cities) + cities_per_page - 1) // cities_per_page
    start_idx = page * cities_per_page
    end_idx = min(start_idx + cities_per_page, len(all_cities))
    
    # Города текущей страницы (по 2 в ряд)
    page_cities = all_cities[start_idx:end_idx]
    for i in range(0, len(page_cities), 2):
        if i + 1 < len(page_cities):
            builder.row(
                InlineKeyboardButton(text=page_cities[i][0], callback_data=page_cities[i][1]),
                InlineKeyboardButton(text=page_cities[i+1][0], callback_data=page_cities[i+1][1])
            )
        else:
            builder.row(InlineKeyboardButton(text=page_cities[i][0], callback_data=page_cities[i][1]))
    
    # Кнопки навигации
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(text="◀️ Назад", callback_data=f"cities_page:{page-1}"))
    nav_buttons.append(InlineKeyboardButton(text=f"{page+1}/{total_pages}", callback_data="noop"))
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton(text="Вперёд ▶️", callback_data=f"cities_page:{page+1}"))
    
    if nav_buttons:
        builder.row(*nav_buttons)
    
    builder.row(InlineKeyboardButton(text="🏠 В меню", callback_data="back_to_menu"))
    
    return builder.as_markup()


def get_category_keyboard(for_subscription: bool = False) -> InlineKeyboardMarkup:
    """Клавиатура выбора категории"""
    builder = InlineKeyboardBuilder()
    
    prefix = "subscribe:" if for_subscription else "category:"
    
    categories = [
        ("🍎 Продукты", f"{prefix}grocery"),
        ("👕 Одежда", f"{prefix}clothing"),
        ("📱 Техника", f"{prefix}electronics"),
        ("🏠 Товары для дома", f"{prefix}home"),
    ]
    
    for cat_name, callback_data in categories:
        builder.row(InlineKeyboardButton(text=cat_name, callback_data=callback_data))
    
    builder.row(InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu"))
    
    return builder.as_markup()


def get_discounts_keyboard(category: str) -> InlineKeyboardMarkup:
    """Клавиатура для просмотра скидок"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_discounts"),
        InlineKeyboardButton(text="🔔 Подписаться", callback_data=f"subscribe:{category}")
    )
    builder.row(InlineKeyboardButton(text="◀️ К категориям", callback_data="back_to_categories"))
    
    return builder.as_markup()


def get_back_keyboard() -> InlineKeyboardMarkup:
    """Кнопка назад"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu"))
    return builder.as_markup()


def get_store_keyboard(store_url: str | None = None) -> InlineKeyboardMarkup:
    """Клавиатура для магазина"""
    builder = InlineKeyboardBuilder()
    
    if store_url:
        builder.row(InlineKeyboardButton(text="🌐 Открыть сайт", url=store_url))
    
    builder.row(InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_categories"))
    
    return builder.as_markup()
