"""
Константы приложения: цвета, шрифты, размеры
"""

# ==================== ЦВЕТА ====================
class COLORS:
    """Цветовая палитра приложения"""
    # Основные цвета фона
    BG_DARK = "#1a1a1a"
    BG_MEDIUM = "#2b2b2b"
    BG_LIGHT = "#404040"
    BG_TITLEBAR = "#1e1e1e"
    
    # Цвета текста
    TEXT_PRIMARY = "#ffffff"
    TEXT_SECONDARY = "#e0e0e0"
    TEXT_MUTED = "#a0a0a0"
    TEXT_DISABLED = "#808080"
    
    # Акцентные цвета
    ACCENT_GREEN = "#4CAF50"
    ACCENT_GREEN_HOVER = "#45a049"
    ACCENT_RED = "#d32f2f"
    ACCENT_RED_HOVER = "#b71c1c"
    ACCENT_BLUE = "#2196F3"
    
    # Цвета границ
    BORDER_DEFAULT = "#404040"
    BORDER_FOCUS = "#505050"
    
    # Цвета состояний
    SUCCESS = "#90EE90"
    ERROR = "#FF6B6B"
    WARNING = "#FFA500"
    INFO = "#64B5F6"
    
    # Hover эффекты
    HOVER_DARK = "#404040"
    HOVER_LIGHT = "#505050"
    HOVER_DANGER = "#e81123"


# ==================== ШРИФТЫ ====================
class FONTS:
    """Настройки шрифтов приложения"""
    FAMILY = "Segoe UI"
    FAMILY_EMOJI = "Segoe UI Emoji"
    
    # Размеры и стили
    TITLE = (FAMILY, 14, "bold")
    SUBTITLE = (FAMILY, 12, "bold")
    BUTTON_EMOJI = (FAMILY_EMOJI, 13)
    BUTTON = (FAMILY, 12)
    LABEL = (FAMILY, 11)
    SMALL = (FAMILY, 10)
    TEXT = (FAMILY_EMOJI, 12)
    HEADER = (FAMILY, 18, "bold")


# ==================== РАЗМЕРЫ ====================
class SIZES:
    """Размеры элементов интерфейса"""
    # Окна
    WINDOW_WIDTH = 1000
    WINDOW_HEIGHT = 800
    WINDOW_MIN_WIDTH = 800
    WINDOW_MIN_HEIGHT = 600
    
    # Диалоги
    DIALOG_SMALL_WIDTH = 350
    DIALOG_SMALL_HEIGHT = 175
    DIALOG_MEDIUM_WIDTH = 400
    DIALOG_MEDIUM_HEIGHT = 215
    DIALOG_LARGE_WIDTH = 450
    DIALOG_LARGE_HEIGHT = 235
    DIALOG_XLARGE_WIDTH = 750
    DIALOG_XLARGE_HEIGHT = 700
    
    # Элементы управления
    TITLEBAR_HEIGHT = 40
    STATUS_BAR_HEIGHT = 40
    BUTTON_HEIGHT = 32
    BUTTON_LARGE_HEIGHT = 36
    
    # Кнопки
    BUTTON_WIDTH_SMALL = 100
    BUTTON_WIDTH_MEDIUM = 130
    BUTTON_WIDTH_LARGE = 150
    BUTTON_ICON_SIZE = 45
    BUTTON_CLOSE_SIZE = 35
    
    # Отступы
    PADDING_SMALL = 5
    PADDING_MEDIUM = 10
    PADDING_LARGE = 15
    PADDING_XLARGE = 20
    
    # Скругления
    CORNER_RADIUS_SMALL = 6
    CORNER_RADIUS_MEDIUM = 8
    CORNER_RADIUS_LARGE = 10
    
    # Текстовые поля
    TEXTBOX_HEIGHT_SMALL = 2
    TEXTBOX_HEIGHT_MEDIUM = 18
    TEXTBOX_WIDTH = 70
    TEMPLATE_DISPLAY_HEIGHT = 150


# ==================== КОНФИГУРАЦИЯ UI ====================
class UI_CONFIG:
    """Общие настройки интерфейса"""
    APPEARANCE_MODE = "dark"
    COLOR_THEME = "dark-blue"
    
    # Скролл
    SCROLL_SPEED = 3
    
    # Canvas
    CANVAS_HIGHLIGHTTHICKNESS = 0
    
    # Анимации (если будут)
    ANIMATION_DURATION = 200  # ms
    
    # Статус-бар
    STATUS_MESSAGE_DURATION = 2000  # ms
