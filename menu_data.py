# menu_data.py

MENU = {
    'main_menu': {
        'title': 'Добро пожаловать в наш магазин вышивки! 🧵\nВыберите интересующую вас категорию:',
        'type': 'list', # Can be 'list' or 'button'
        'options': [
            {'id': 'cat_kits', 'title': 'Наборы для вышивки', 'description': 'Готовые комплекты для творчества', 'next_menu_id': 'menu_kits'},
            {'id': 'cat_threads', 'title': 'Нитки для вышивки', 'description': 'Мулине различных производителей', 'next_menu_id': 'menu_threads'},
            # {'id': 'view_cart', 'title': '🛒 Посмотреть корзину', 'action': 'view_cart'}, # Future implementation
            {'id': 'contact_manager', 'title': '📞 Связаться с менеджером', 'action': 'contact_manager'}
        ]
    },
    'menu_kits': {
        'title': 'Наборы для вышивки. Выберите товар:',
        'type': 'list',
        'options': [
            {'id': 'kit_sf', 'title': 'Набор "Весенние цветы"', 'description': 'Яркий и красивый набор.', 'price': 1500, 'action': 'select_item'},
            {'id': 'kit_wl', 'title': 'Набор "Зимний пейзаж"', 'description': 'Успокаивающая зимняя тематика.', 'price': 1800, 'action': 'select_item'},
            {'id': 'kit_mg', 'title': 'Набор "Магический лес"', 'description': 'Фэнтезийный сюжет.', 'price': 1650, 'action': 'select_item'},
            {'id': 'back_to_main_kits', 'title': '⬅️ Назад в главное меню', 'next_menu_id': 'main_menu'} # Unique ID for back option
        ]
    },
    'menu_threads': {
        'title': 'Нитки для вышивки. Выберите товар:',
        'type': 'list',
        'options': [
            {'id': 'thread_dmc_24', 'title': 'Набор мулине DMC (24 цвета)', 'description': 'Высококачественные хлопковые нитки.', 'price': 900, 'action': 'select_item'},
            {'id': 'thread_anchor_mix', 'title': 'Микс мулине Anchor (12 шт)', 'description': 'Яркие цвета для ваших проектов.', 'price': 450, 'action': 'select_item'},
            {'id': 'back_to_main_threads', 'title': '⬅️ Назад в главное меню', 'next_menu_id': 'main_menu'} # Unique ID for back option
        ]
    },
    # --- Special Menus/Messages ---
    'contact_manager_message': { # This is not a menu, but a message to be sent by an action
        'type': 'text',
        'text': 'Спасибо за ваше обращение! Менеджер скоро свяжется с вами по WhatsApp.'
    },
    'item_selected_confirmation': { # Dynamic text, parts will be filled in
        'type': 'text',
        'text': '✅ "{item_name}" добавлен(о) в вашу корзину (Цена: {item_price} руб).\n\nВыберите что-нибудь еще или вернитесь в главное меню.'
    },
    'default_fallback_message': {
        'type': 'text',
        'text': 'Извините, я не понял ваш запрос. Пожалуйста, используйте кнопки меню для навигации или введите "меню", чтобы начать сначала.'
    },
    'cart_view_message': { # Placeholder for cart view
        'type': 'text',
        'text': 'Ваша корзина:\n{cart_items}\n\nОбщая сумма: {total_price} руб.'
    }
}

# Helper function to get a menu item by its ID
def get_menu(menu_id):
    return MENU.get(menu_id)

# Helper function to get an option from a menu by its ID
def get_option_by_id(menu_id, option_id):
    menu = get_menu(menu_id)
    if menu:
        for option in menu.get('options', []):
            if option['id'] == option_id:
                return option
    return None
```
