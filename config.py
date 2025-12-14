# config.py

# Screen settings
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 800
FPS = 60

# Global scale factor
SCALE_FACTOR = 1.1

def get_scaled_value(value):
    return int(value * SCALE_FACTOR)

# Base positions
BASE_SELECTION_X_RATIO = 0.25
BASE_SELECTION_Y = 225
BASE_SUBCATEGORY_SELECTION_Y = 285
BASE_OPTION_SELECTION_Y = 325

# Scaled positions
SELECTION_X = get_scaled_value(SCREEN_WIDTH * BASE_SELECTION_X_RATIO)
SELECTION_Y = get_scaled_value(BASE_SELECTION_Y)
SUBCATEGORY_SELECTION_Y = get_scaled_value(BASE_SUBCATEGORY_SELECTION_Y)
OPTION_SELECTION_Y = get_scaled_value(BASE_OPTION_SELECTION_Y)

# ============================================================================
# КАТЕГОРИИ - отдельные настройки
# ============================================================================
CATEGORY_ICON_SIZE = (get_scaled_value(80), get_scaled_value(80))  # Размер иконок категорий
CATEGORY_FONT_SIZE = get_scaled_value(15)                         # Размер текста категорий
CATEGORY_GLOW_SIZES = [                                           # Размеры свечения для категорий
    get_scaled_value(60), 
    get_scaled_value(70), 
    get_scaled_value(80)
]

# Позиции для категорий
CATEGORY_ICON_X_OFFSET = get_scaled_value(-40)
CATEGORY_ICON_Y_OFFSET = get_scaled_value(-70)
CATEGORY_TEXT_Y_OFFSET = get_scaled_value(10)

# ============================================================================
# ПОДКАТЕГОРИИ - отдельные настройки  
# ============================================================================
SUBCATEGORY_ICON_SIZE = (get_scaled_value(45), get_scaled_value(45))  # Размер иконок подкатегорий
SUBCATEGORY_FONT_SIZE = get_scaled_value(20)                         # Размер текста подкатегорий
SUBCATEGORY_GLOW_SIZES = [                                           # Размеры свечения для подкатегорий
    get_scaled_value(55), 
    get_scaled_value(65), 
    get_scaled_value(75)
]

# Позиции для подкатегорий
SUBCATEGORY_X_OFFSET = get_scaled_value(-25)
SUBCATEGORY_ICON_Y_OFFSET = get_scaled_value(-30)
SUBCATEGORY_TEXT_X_OFFSET = get_scaled_value(65)
SUBCATEGORY_TEXT_Y_OFFSET = get_scaled_value(-5)

# ============================================================================
# ОПЦИИ - отдельные настройки
# ============================================================================
OPTION_ICON_SIZE = (get_scaled_value(40), get_scaled_value(40))      # Размер иконок опций
OPTION_FONT_SIZE = get_scaled_value(28)                             # Размер текста опций
OPTION_GLOW_SIZES = [                                               # Размеры свечения для опций
    get_scaled_value(50), 
    get_scaled_value(60), 
    get_scaled_value(70)
]

# Позиции для опций
OPTION_X_OFFSET = get_scaled_value(300)
OPTION_ICON_X_OFFSET = get_scaled_value(-30)
OPTION_ICON_Y_OFFSET = get_scaled_value(-30)
OPTION_TEXT_X_OFFSET = get_scaled_value(40)
OPTION_TEXT_Y_OFFSET = get_scaled_value(0)

# ============================================================================
# ОБЩИЕ НАСТРОЙКИ
# ============================================================================
# Spacing values
CATEGORY_SPACING = get_scaled_value(120)
SUBCATEGORY_SPACING = get_scaled_value(65)
SUBCATEGORY_SELECTED_EXTRA_SPACING = get_scaled_value(90)
OPTION_SPACING = get_scaled_value(65)

# Animation speeds
ANIMATION_SPEED = 0.2
FADE_SPEED = 0.1
PULSE_SPEED = 0.01
OFFSET_SPEED = 0.2

# Interface offset
INTERFACE_OFFSET_AMOUNT = get_scaled_value(200)

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
SILVER = (192, 192, 192)
LIGHT_SILVER = (220, 220, 220)
SELECTED_COLOR = (255, 255, 0)
GLOW_COLOR = (255, 255, 255, 180)

# Navigation levels
NAV_LEVEL_CATEGORIES = 0
NAV_LEVEL_SUBCATEGORIES = 1
NAV_LEVEL_OPTIONS = 2

# Info panel
INFO_PANEL_X = get_scaled_value(20)
INFO_PANEL_Y = SCREEN_HEIGHT - get_scaled_value(30)
INFO_FONT_SIZE = get_scaled_value(20)

# Built-in categories
BUILTIN_CATEGORIES = [
    {
        "name": "Home",
        "icon": "cat_home.png"
    },
    {
        "name": "Settings", 
        "icon": "cat_settings.png"
    },
    {
        "name": "Photo",
        "icon": "cat_photo.png"
    },
    {
        "name": "Music",
        "icon": "cat_music.png"
    },
    {
        "name": "Video",
        "icon": "cat_video.png"
    },
    {
        "name": "Game",
        "icon": "cat_game.png"
    },
    {
        "name": "Network",
        "icon": "cat_network.png"
    }
]

# Built-in subcategories
BUILTIN_SUBCATEGORIES = {
    "Power Off": {
        "category": "Home",
        "icon": "power_off.png",
        "type": 0,
        "command": "quit"
    },
    "Update Steam Game List": {
        "category": "Game",
        "icon": "update.png",
        "type": 0,
        "command": "python scripts/update_steam_games.py" 
    }
}

# Startup animation settings
STARTUP_BLACK = 2.0  # seconds for black
STARTUP_DISPLAY_DURATION = 1.0  # seconds to display logo
STARTUP_FADE_OUT_DURATION = 3.5  # seconds for fade out
STARTUP_SD_FONT_SIZE = get_scaled_value(120)
STARTUP_STEAM_DECK_FONT_SIZE = get_scaled_value(40)
STARTUP_TEXT_RIGHT_MARGIN = get_scaled_value(100)