"""
Главное окно приложения Template Helper
"""
import customtkinter as ctk
from typing import TYPE_CHECKING
import threading
import json
from pathlib import Path
import sys

if TYPE_CHECKING:
    from models.template_manager import TemplateManager

from views.template_widgets import CategoryHeader, TemplateWidget
from utils.clipboard import copy_to_clipboard
from utils.updater import AppUpdater
from utils.icon_generator import EmojiIconButton
from models.search_indexer import get_search_indexer
from config.constants import COLORS, FONTS, SIZES
from config.settings import MESSAGES, EMOJI, PATHS, APP_NAME, APP_AUTHOR


class MainWindow:
    """
    Главное окно приложения Template Helper
    
    Attributes:
        root: Корневое окно CTk
        template_manager: Менеджер шаблонов
        is_always_on_top: Флаг режима "всегда поверх"
    """
    
    def __init__(self, root: ctk.CTk, template_manager: 'TemplateManager'):
        self.root = root
        self.template_manager = template_manager
        self.is_always_on_top = False
        self.search_query = ""  # Переменная для хранения текста поиска
        
        # Инициализируем поисковый индекс
        self.search_indexer = get_search_indexer()
        
        # Флаги для предотвращения множественного открытия одних и тех же диалогов
        self.add_template_dialog_open = False
        self.edit_template_dialog_open = False
        self.add_category_dialog_open = False
        self.edit_category_dialog_open = False
        self.settings_dialog_open = False
        self.statistics_dialog_open = False
        
        # Кэш для оптимизации UI
        self._widget_cache = {}
        self._last_displayed_category = None
        self._last_search_query = None
        self._search_update_timer = None  # Таймер для debounce поиска
        
        self.setup_window()
        self.setup_ui()
        
        # Предзагрузка иконок в фоне для ускорения UI
        self.root.after(100, EmojiIconButton.preload_common_icons)
        
        self.update_templates_display()
        
        # Проверка обновлений при запуске
        self.check_updates_on_startup()
    
    @staticmethod
    def get_app_version():
        """Получить версию приложения"""
        # Сначала пытаемся импортировать из version.py
        try:
            from config.version import VERSION
            return VERSION
        except ImportError:
            pass
        
        # Fallback - читаем из version.json
        try:
            # Определяем путь к version.json
            if getattr(sys, 'frozen', False):
                # PyInstaller
                if hasattr(sys, '_MEIPASS'):
                    version_path = Path(sys._MEIPASS) / "version.json"
                else:
                    version_path = Path(sys.executable).parent / "version.json"
            else:
                # Если запущен как скрипт
                version_path = Path(__file__).parent.parent / "version.json"
            
            if version_path.exists():
                with open(version_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('version', '0.0.1')
        except Exception as e:
            print(f"Ошибка при получении версии: {e}")
        
        return "0.0.1"
    
    def setup_context_menu_for_widget(self, widget: ctk.CTkBaseClass) -> None:
        """Добавить горячие клавиши для текстового виджета"""
        # Добавляем горячие клавиши
        def make_copy_handler():
            def copy_handler(event=None):
                try:
                    if isinstance(widget, ctk.CTkTextbox):
                        text = widget.tag_ranges("sel")
                        if text:
                            text_content = widget.get(text[0], text[1])
                            self.root.clipboard_clear()
                            self.root.clipboard_append(text_content)
                            self.root.update()
                    return "break"
                except Exception:
                    return "break"
            return copy_handler
        
        def make_paste_handler():
            def paste_handler(event=None):
                try:
                    text = self.root.clipboard_get()
                    if isinstance(widget, ctk.CTkTextbox):
                        widget.insert(ctk.END, text)
                    return "break"
                except Exception:
                    return "break"
            return paste_handler
        
        def make_cut_handler():
            def cut_handler(event=None):
                try:
                    if isinstance(widget, ctk.CTkTextbox):
                        text = widget.tag_ranges("sel")
                        if text:
                            text_content = widget.get(text[0], text[1])
                            widget.delete(text[0], text[1])
                            self.root.clipboard_clear()
                            self.root.clipboard_append(text_content)
                            self.root.update()
                    return "break"
                except Exception:
                    return "break"
            return cut_handler
        
        def make_select_all_handler():
            def select_all_handler(event=None):
                if isinstance(widget, ctk.CTkTextbox):
                    widget.tag_add("sel", "1.0", ctk.END)
                elif isinstance(widget, ctk.CTkEntry):
                    widget.select_range(0, ctk.END)
                return "break"
            return select_all_handler
        
        # Горячие клавиши
        widget.bind('<Control-c>', make_copy_handler())
        widget.bind('<Control-v>', make_paste_handler())
        widget.bind('<Control-x>', make_cut_handler())
        widget.bind('<Control-a>', make_select_all_handler())
    
    def setup_window(self) -> None:
        """Настройка главного окна приложения"""
        self.root.title(APP_NAME)
        
        # Загружаем иконку для окна
        try:
            icon_paths = PATHS.get_icon_paths()
            icon_path = None
            
            for path in icon_paths:
                if path and path.exists():
                    icon_path = path
                    break
            
            if icon_path:
                try:
                    self.root.iconbitmap(str(icon_path))
                except Exception as e:
                    pass
            
        except Exception as e:
            pass
        
        # Получаем размеры экрана
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Центрируем окно
        x = (screen_width - SIZES.WINDOW_WIDTH) // 2
        y = (screen_height - SIZES.WINDOW_HEIGHT) // 2
        
        # Устанавливаем геометрию
        self.root.geometry(f'{SIZES.WINDOW_WIDTH}x{SIZES.WINDOW_HEIGHT}+{x}+{y}')
        
        # Устанавливаем минимальный размер окна
        self.root.minsize(SIZES.WINDOW_MIN_WIDTH, SIZES.WINDOW_MIN_HEIGHT)
        
        print("[DEBUG] Используем стандартные рамки Windows")
    
    def setup_ui(self) -> None:
        """Создание современного пользовательского интерфейса"""
        # Создание кастомной заголовочной панели (для окна без рамок)
        self.create_custom_titlebar()
        
        # Основной фрейм с отступом сверху
        main_frame = ctk.CTkFrame(self.root, fg_color=COLORS.BG_DARK)
        main_frame.pack(fill=ctk.BOTH, expand=True, padx=0, pady=(SIZES.PADDING_MEDIUM, 0))
        
        # Заголовок с категориями
        self.category_header = CategoryHeader(
            parent=main_frame,
            categories=self.template_manager.get_categories(),
            category_types=self.template_manager.get_category_types(),
            on_category_select=self.on_category_selected,
            on_category_type_select=self.on_category_type_selected,
            on_add_category=self.add_category,
            on_edit_category=self.edit_category,
            on_add_template=self.add_template
        )
        
        # Панель "Work In Progress" с кнопками инструментов
        self.setup_wip_panel(main_frame)
        
        # Область отображения шаблонов
        self.templates_frame = ctk.CTkFrame(main_frame, fg_color=COLORS.BG_DARK)
        self.templates_frame.pack(fill=ctk.BOTH, expand=True, padx=SIZES.PADDING_MEDIUM, pady=SIZES.PADDING_MEDIUM)
        
        # Статус-бар в правом нижнем углу
        self.setup_status_bar(main_frame)
        
        # Принудительно обновляем отображение для первой категории
        self.root.after(100, self.on_category_selected)
    
    def setup_status_bar(self, parent):
        """Настройка статус-бара"""
        status_frame = ctk.CTkFrame(parent, fg_color=COLORS.BG_MEDIUM, height=SIZES.STATUS_BAR_HEIGHT)
        status_frame.pack(fill=ctk.X, side=ctk.BOTTOM)
        status_frame.pack_propagate(False)
        
        # Левая часть статус-бара
        self.status_left = ctk.CTkLabel(
            status_frame, 
            text=MESSAGES.STATUS_READY, 
            text_color=COLORS.TEXT_MUTED,
            font=FONTS.SMALL
        )
        self.status_left.pack(side=ctk.LEFT, padx=SIZES.PADDING_MEDIUM, pady=SIZES.PADDING_MEDIUM)
        
        # Правая часть статус-бара (для временных уведомлений)
        self.status_right = ctk.CTkLabel(
            status_frame, 
            text="", 
            text_color=COLORS.SUCCESS,
            font=FONTS.SMALL
        )
        self.status_right.pack(side=ctk.RIGHT, padx=SIZES.PADDING_MEDIUM, pady=SIZES.PADDING_MEDIUM)
    
    def show_status_message(self, message: str, duration: int = 2000):
        """Показать временное сообщение в статус-баре"""
        self.status_right.configure(text=message, text_color=COLORS.SUCCESS)
        
        # Используем after вместо threading для лучшей производительности
        self.root.after(duration, lambda: self.status_right.configure(text=""))
    
    def setup_wip_panel(self, parent) -> None:
        """Настройка панели поиска"""
        search_frame = ctk.CTkFrame(parent, fg_color=COLORS.BG_MEDIUM, corner_radius=SIZES.CORNER_RADIUS_LARGE)
        search_frame.pack(fill=ctk.X, padx=SIZES.PADDING_MEDIUM, pady=(0, SIZES.PADDING_MEDIUM))
        
        # Иконка поиска (Twemoji)
        search_icon_img = EmojiIconButton.get_ctk_image("🔍", size=16)
        search_icon = ctk.CTkLabel(
            search_frame,
            text="",
            image=search_icon_img,
            text_color=COLORS.TEXT_SECONDARY
        )
        search_icon.pack(side=ctk.LEFT, padx=(SIZES.PADDING_LARGE, 5), pady=SIZES.PADDING_MEDIUM)
        
        # Поле поиска
        self.search_var = ctk.StringVar()
        self.search_var.trace("w", lambda name, index, mode: self.filter_templates_by_search(self.search_var.get()))
        
        search_entry = ctk.CTkEntry(
            search_frame,
            textvariable=self.search_var,
            placeholder_text="Поиск по названию или содержимому...",
            font=FONTS.TEXT,
            fg_color=COLORS.BG_LIGHT,
            text_color=COLORS.TEXT_PRIMARY,
            border_color=COLORS.BORDER_DEFAULT,
            border_width=1,
            corner_radius=SIZES.CORNER_RADIUS_SMALL,
            height=32
        )
        search_entry.pack(side=ctk.LEFT, fill=ctk.X, expand=True, padx=(0, SIZES.PADDING_LARGE), pady=SIZES.PADDING_MEDIUM)
    
    def filter_templates_by_search(self, search_text: str) -> None:
        """Фильтрация шаблонов по тексту поиска с debounce"""
        # Отменяем предыдущий таймер обновления
        if self._search_update_timer:
            self.root.after_cancel(self._search_update_timer)
        
        # Сохраняем запрос
        self.search_query = search_text.lower().strip()
        
        # Запускаем обновление через 300мс (после паузы в наборе)
        self._search_update_timer = self.root.after(300, self._delayed_update)
    
    def _delayed_update(self) -> None:
        """Отложенное обновление после паузы в наборе"""
        self._search_update_timer = None
        self.update_templates_display()
    
    def show_statistics_dialog(self) -> None:
        """Показать диалоговое окно со статистикой всех шаблонов"""
        # Проверка: если диалог уже открыт, не создавать новый
        if self.statistics_dialog_open:
            return
        
        current_category = self.category_header.get_selected_category()
        if not current_category:
            self.show_status_message("Выберите категорию сначала")
            return
        
        # Получаем все шаблоны и сортируем по количеству копирований
        all_templates = self.template_manager.get_templates(current_category)
        sorted_templates = sorted(
            all_templates, 
            key=lambda t: t.get('stats', {}).get('usage_count', 0), 
            reverse=True
        )
        
        # Фильтруем только те, у которых есть статистика
        templates_with_stats = [t for t in sorted_templates if t.get('stats', {}).get('usage_count', 0) > 0]
        
        if not templates_with_stats:
            self.show_status_message("Статистика ещё недоступна")
            return
        
        self.statistics_dialog_open = True
        
        # Обработчик закрытия окна
        def on_close():
            self.statistics_dialog_open = False
        
        # Создаём диалоговое окно
        stats_dialog = ctk.CTkToplevel(self.root)
        stats_dialog.title("Статистика")
        stats_dialog.geometry("600x500")
        stats_dialog.protocol("WM_DELETE_WINDOW", lambda: [on_close(), stats_dialog.destroy()])
        
        # Устанавливаем иконку
        try:
            icon_paths = PATHS.get_icon_paths()
            for path in icon_paths:
                if path and path.exists():
                    stats_dialog.iconbitmap(str(path))
                    break
        except:
            pass
        
        # Убеждаемся что окно будет поверх всегда
        stats_dialog.attributes("-topmost", True)
        stats_dialog.after(100, lambda: stats_dialog.lift())
        stats_dialog.after(100, lambda: stats_dialog.focus_force())
        
        stats_dialog.resizable(False, False)
        
        # Основной фрейм
        main_frame = ctk.CTkFrame(stats_dialog, fg_color="transparent")
        main_frame.pack(fill=ctk.BOTH, expand=True, padx=20, pady=20)
        
        # Заголовок
        title_label = ctk.CTkLabel(
            main_frame,
            text=f"Статистика копирований в '{current_category}'",
            font=("Segoe UI", 14, "bold"),
            text_color="#FFFFFF"
        )
        title_label.pack(anchor="w", pady=(0, 15))
        
        # Создаём скролируемый фрейм для списка шаблонов
        scrollable_frame = ctk.CTkScrollableFrame(
            main_frame,
            fg_color="transparent",
            corner_radius=6
        )
        scrollable_frame.pack(fill=ctk.BOTH, expand=True, pady=(0, 15))
        
        # Список всех шаблонов со статистикой
        for idx, template in enumerate(templates_with_stats, 1):
            usage_count = template.get('stats', {}).get('usage_count', 0)
            
            item_frame = ctk.CTkFrame(scrollable_frame, fg_color="transparent")
            item_frame.pack(fill=ctk.X, pady=8)
            
            # Ранг
            rank_label = ctk.CTkLabel(
                item_frame,
                text=f"#{idx}",
                font=("Segoe UI", 11, "bold"),
                text_color="#FFD700",
                width=30
            )
            rank_label.pack(side=ctk.LEFT, padx=(0, 10))
            
            # Название
            title = ctk.CTkLabel(
                item_frame,
                text=template.get('title', 'Template'),
                font=("Segoe UI", 11),
                text_color="#FFFFFF",
                anchor="w"
            )
            title.pack(side=ctk.LEFT, fill=ctk.X, expand=True)
            
            # Счётчик
            count_label = ctk.CTkLabel(
                item_frame,
                text=f"{usage_count}x",
                font=("Segoe UI", 11, "bold"),
                text_color="#1E90FF"
            )
            count_label.pack(side=ctk.RIGHT, padx=(10, 0))
        
        # Кнопка закрытия
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill=ctk.X, pady=(0, 0))
        
        close_btn = ctk.CTkButton(
            btn_frame,
            text="Закрыть",
            command=lambda: [on_close(), stats_dialog.destroy()],
            width=100,
            height=32
        )
        close_btn.pack(side=ctk.RIGHT)
        
        # Горячие клавиши
        stats_dialog.bind('<Escape>', lambda e: [on_close(), stats_dialog.destroy()])
        stats_dialog.bind('<Return>', lambda e: [on_close(), stats_dialog.destroy()])
        
        # Центрируем окно
        stats_dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (stats_dialog.winfo_width() // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (stats_dialog.winfo_height() // 2)
        stats_dialog.geometry(f"+{x}+{y}")
    
    def show_settings_dialog(self) -> None:
        """Показать диалоговое окно с настройками"""
        # Проверка: если диалог уже открыт, не создавать новый
        if self.settings_dialog_open:
            return
        
        self.settings_dialog_open = True
        
        # Обработчик закрытия окна
        def on_close():
            self.settings_dialog_open = False
        
        # Создаём диалоговое окно
        settings_dialog = ctk.CTkToplevel(self.root)
        settings_dialog.title("Настройки")
        settings_dialog.geometry("400x250")
        settings_dialog.protocol("WM_DELETE_WINDOW", lambda: [on_close(), settings_dialog.destroy()])
        
        # Устанавливаем иконку
        try:
            icon_paths = PATHS.get_icon_paths()
            for path in icon_paths:
                if path and path.exists():
                    settings_dialog.iconbitmap(str(path))
                    break
        except:
            pass
        
        # Убеждаемся что окно будет поверх всегда
        settings_dialog.attributes("-topmost", True)
        settings_dialog.after(100, lambda: settings_dialog.lift())
        settings_dialog.after(100, lambda: settings_dialog.focus_force())
        
        settings_dialog.resizable(False, False)
        
        # Основной фрейм
        main_frame = ctk.CTkFrame(settings_dialog, fg_color="transparent")
        main_frame.pack(fill=ctk.BOTH, expand=True, padx=20, pady=20)
        
        # Заголовок
        title_label = ctk.CTkLabel(
            main_frame,
            text="Настройки приложения",
            font=("Segoe UI", 14, "bold"),
            text_color="#FFFFFF"
        )
        title_label.pack(anchor="w", pady=(0, 20))
        
        # Раздел статистики
        stats_section = ctk.CTkLabel(
            main_frame,
            text="Статистика:",
            font=("Segoe UI", 11, "bold"),
            text_color="#FFFFFF"
        )
        stats_section.pack(anchor="w", pady=(0, 10))
        
        # Кнопка сброса статистики
        def reset_statistics():
            current_category = self.category_header.get_selected_category()
            if current_category:
                self.template_manager.reset_statistics(current_category)
                self.show_status_message("✓ Статистика сброшена")
                self.force_update_templates_display()
                on_close()
                settings_dialog.destroy()
        
        reset_btn = ctk.CTkButton(
            main_frame,
            text="Сбросить статистику",
            command=reset_statistics,
            height=32,
            fg_color="#ff6b6b",
            hover_color="#ff5252",
            text_color="#FFFFFF"
        )
        reset_btn.pack(fill=ctk.X, pady=5)
        
        # Кнопка закрытия
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill=ctk.X, pady=(20, 0))
        
        close_btn = ctk.CTkButton(
            btn_frame,
            text="Закрыть",
            command=lambda: [on_close(), settings_dialog.destroy()],
            width=100,
            height=32
        )
        close_btn.pack(side=ctk.RIGHT)
        
        # Горячие клавиши
        settings_dialog.bind('<Escape>', lambda e: [on_close(), settings_dialog.destroy()])
        
        # Центрируем окно
        settings_dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (settings_dialog.winfo_width() // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (settings_dialog.winfo_height() // 2)
        settings_dialog.geometry(f"+{x}+{y}")
    
    def create_custom_dialog(self, title: str, width: int, height: int, on_close_callback=None) -> ctk.CTkToplevel:
        """Создает диалоговое окно с кастомным заголовком без рамок"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title(title)
        dialog.overrideredirect(True)
        dialog.geometry(f"{width}x{height}")
        
        # Если главное окно закреплено, то закрепляем и диалог
        if self.is_always_on_top:
            dialog.wm_attributes("-topmost", True)
        
        # Центрирование диалога
        dialog.update_idletasks()
        x = (self.root.winfo_x() + (self.root.winfo_width() // 2)) - (width // 2)
        y = (self.root.winfo_y() + (self.root.winfo_height() // 2)) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        # Контейнер с обводкой для всего диалога
        border_frame = ctk.CTkFrame(
            dialog,
            fg_color="#1a1a1a",
            border_width=1,
            border_color="#1e1e1e",
            corner_radius=0
        )
        border_frame.pack(fill=ctk.BOTH, expand=True)
        
        # Создаем кастомный заголовок для диалога
        dialog_titlebar = ctk.CTkFrame(
            border_frame,
            fg_color="#1e1e1e",
            corner_radius=0,
            height=35
        )
        dialog_titlebar.pack(side=ctk.TOP, fill=ctk.X)
        dialog_titlebar.pack_propagate(False)
        
        # Название диалога
        dialog_title_label = ctk.CTkLabel(
            dialog_titlebar,
            text=title,
            font=("Segoe UI", 12, "bold"),
            text_color="#e0e0e0"
        )
        dialog_title_label.pack(side=ctk.LEFT, padx=12, pady=0)
        
        # Кнопка закрытия диалога
        def close_dialog():
            if on_close_callback:
                on_close_callback()
            dialog.destroy()
        
        dialog_close_button = ctk.CTkButton(
            dialog_titlebar,
            text="✕",
            font=("Arial", 14, "bold"),
            width=35,
            height=35,
            fg_color="transparent",
            hover_color="#e81123",
            text_color="#e0e0e0",
            command=close_dialog,
            corner_radius=0,
            border_width=0
        )
        dialog_close_button.pack(side=ctk.RIGHT)
        
        # Функциональность перемещения диалога
        dialog_drag_data = {"x": 0, "y": 0}
        
        def start_dialog_move(event):
            dialog_drag_data["x"] = event.x_root - dialog.winfo_x()
            dialog_drag_data["y"] = event.y_root - dialog.winfo_y()
        
        def do_dialog_move(event):
            x = event.x_root - dialog_drag_data["x"]
            y = event.y_root - dialog_drag_data["y"]
            dialog.geometry(f"+{x}+{y}")
        
        dialog_titlebar.bind("<Button-1>", start_dialog_move)
        dialog_titlebar.bind("<B1-Motion>", do_dialog_move)
        dialog_title_label.bind("<Button-1>", start_dialog_move)
        dialog_title_label.bind("<B1-Motion>", do_dialog_move)
        
        # Сохраняем ссылку на border_frame для добавления контента
        dialog.content_frame = border_frame
        
        return dialog
    
    def create_custom_titlebar(self) -> None:
        """Создает кастомную заголовочную панель с замочком и информацией"""
        # Фрейм для заголовка
        titlebar = ctk.CTkFrame(
            self.root,
            fg_color="#1e1e1e",
            corner_radius=0,
            height=40,
            border_width=0
        )
        titlebar.pack(side=ctk.TOP, fill=ctk.X, padx=0, pady=0)
        titlebar.pack_propagate(False)
        
        # Кнопка "Настройки" - только иконка
        settings_image = EmojiIconButton.get_ctk_image("🔨", size=20, bg_color="transparent")
        settings_btn = ctk.CTkButton(
            titlebar,
            text="",
            image=settings_image,
            command=self.show_settings_dialog,
            font=("Segoe UI", 10),
            width=28,
            height=28,
            fg_color="transparent",
            hover_color="#5a5a5a",
            text_color="#ffffff",
            corner_radius=4,
            border_width=0
        )
        settings_btn.pack(side=ctk.LEFT, padx=6, pady=6)
        
        # Разделитель
        separator = ctk.CTkLabel(
            titlebar,
            text="|",
            text_color="#666666",
            font=("Segoe UI", 14)
        )
        separator.pack(side=ctk.LEFT, padx=4, pady=6)
        
        # Кнопка "Статистика" с иконкой
        stats_image = EmojiIconButton.get_ctk_image("📊", size=20, bg_color="transparent")
        stats_btn = ctk.CTkButton(
            titlebar,
            text="Статистика",
            image=stats_image,
            compound="left",
            command=self.show_statistics_dialog,
            font=("Segoe UI", 10),
            width=115,
            height=28,
            fg_color="#4a4a4a",
            hover_color="#5a5a5a",
            text_color="#ffffff",
            corner_radius=4,
            border_width=0
        )
        stats_btn.pack(side=ctk.LEFT, padx=6, pady=6)
        
        # Кнопка закрепления (замочек) - единственная кнопка управления
        self.pin_button = ctk.CTkButton(
            titlebar,
            text=EMOJI.LOCK,
            font=FONTS.BUTTON_EMOJI,
            width=SIZES.BUTTON_ICON_SIZE,
            height=SIZES.TITLEBAR_HEIGHT,
            fg_color="transparent",
            hover_color=COLORS.HOVER_DARK,
            text_color=COLORS.TEXT_DISABLED,
            command=self.toggle_always_on_top,
            corner_radius=0,
            border_width=0
        )
        self.pin_button.pack(side=ctk.RIGHT, padx=5, pady=0)
        
        # Авторство и версия справа (после замочка) - кликабельная ссылка на GitHub
        info_frame = ctk.CTkFrame(titlebar, fg_color="transparent")
        info_frame.pack(side=ctk.RIGHT, padx=15, pady=0)
        
        def open_github():
            import webbrowser
            webbrowser.open("https://github.com/teja1337")
        
        info_button = ctk.CTkButton(
            info_frame,
            text=f"{APP_AUTHOR} | v{self.get_app_version()}",
            font=FONTS.LABEL,
            text_color=COLORS.TEXT_DISABLED,
            fg_color="transparent",
            hover_color=COLORS.HOVER_DARK,
            command=open_github,
            border_width=0,
            corner_radius=4
        )
        info_button.pack(side=ctk.TOP, pady=0)
        
        # Функциональность перемещения окна
        self.drag_data = {"x": 0, "y": 0}
        titlebar.bind("<Button-1>", self.start_move)
        titlebar.bind("<B1-Motion>", self.do_move)
    
    def start_move(self, event):
        """Начинает перемещение окна"""
        self.drag_data["x"] = event.x_root - self.root.winfo_x()
        self.drag_data["y"] = event.y_root - self.root.winfo_y()
    
    def do_move(self, event):
        """Перемещает окно при перетаскивании заголовка"""
        x = event.x_root - self.drag_data["x"]
        y = event.y_root - self.drag_data["y"]
        self.root.geometry(f"+{x}+{y}")
    
    def toggle_always_on_top(self) -> None:
        """Включает/отключает режим 'всегда поверх всех окон'"""
        self.is_always_on_top = not self.is_always_on_top
        self.root.wm_attributes("-topmost", self.is_always_on_top)
        
        # Обновляем цвет кнопки как индикатор статуса
        if self.is_always_on_top:
            self.pin_button.configure(text_color=COLORS.ACCENT_GREEN)  # Зелёный - активно
        else:
            self.pin_button.configure(text_color=COLORS.TEXT_DISABLED)  # Серый - неактивно
    
    def on_category_selected(self, event=None) -> None:
        """Обработчик выбора категории"""
        self.update_templates_display()
        
        # Обновляем левую часть статус-бара
        current_category = self.category_header.get_selected_category()
        if current_category:
            templates_count = len(self.template_manager.get_templates(current_category))
            self.status_left.configure(text=f"Категория: {current_category} | Шаблонов: {templates_count}")
    
    def on_category_type_selected(self, category_type: str) -> None:
        """Обработчик выбора типа категорий"""
        self.template_manager.set_category_type(category_type)
        # Обновляем список категорий
        categories = self.template_manager.get_categories()
        self.category_header.update_categories(categories)
        # Обновляем отображение шаблонов
        if categories:
            self.on_category_selected()
        else:
            # Если категорий нет, очищаем область шаблонов
            self.update_templates_display()
    
    def add_category(self) -> None:
        """Добавление новой категории с современным диалогом"""
        # Проверка: если диалог уже открыт, не создавать новый
        if self.add_category_dialog_open:
            return
        
        self.add_category_dialog_open = True
        
        category_name = self.show_modern_dialog(
            "Новая категория", 
            "Введите название категории:"
        )
        
        self.add_category_dialog_open = False
        
        if category_name:
            if self.template_manager.add_category(category_name):
                # ОПТИМИЗАЦИЯ: Обновляем индекс поиска
                self.search_indexer.build_index(self.template_manager)
                self.category_header.update_categories(self.template_manager.get_categories())
                self.category_header.set_selected_category(category_name)
                self.force_update_templates_display()
                self.show_status_message("✓ Категория добавлена")
            else:
                self.show_status_message("✗ Ошибка добавления категории")
    
    def edit_category(self) -> None:
        """Редактирование текущей категории с опциями переименования и удаления"""
        # Проверка: если диалог уже открыт, не создавать новый
        if self.edit_category_dialog_open:
            return
        
        current_category = self.category_header.get_selected_category()
        if not current_category:
            self.show_status_message("⚠ Сначала выберите категорию")
            return
        
        self.edit_category_dialog_open = True
        
        # Обработчик закрытия окна
        def on_close():
            self.edit_category_dialog_open = False
        
        # Создаем кастомный диалог
        dialog = self.create_custom_dialog("Редактирование категории", 450, 235, on_close_callback=on_close)
        
        # Убираем старый обработчик WM_DELETE_WINDOW
        dialog.protocol("WM_DELETE_WINDOW", on_close)
        
        # Основной фрейм
        main_frame = ctk.CTkFrame(dialog.content_frame, fg_color="#1a1a1a")
        main_frame.pack(fill=ctk.BOTH, expand=True, padx=15, pady=15)
        
        # Заголовок
        title_label = ctk.CTkLabel(
            main_frame,
            text=f"Категория: {current_category}",
            font=("Segoe UI", 16, "bold"),
            text_color="white"
        )
        title_label.pack(anchor="w", pady=(0, 15))
        
        # Поле для переименования
        ctk.CTkLabel(main_frame, text="Новое название:", text_color="white").pack(anchor="w", pady=(10, 3))
        
        name_entry = ctk.CTkTextbox(
            main_frame,
            height=2,
            font=("Segoe UI Emoji", 12),
            text_color="white",
            fg_color="#2b2b2b",
            border_color="#404040",
            border_width=1
        )
        name_entry.pack(fill=ctk.X, pady=(0, 20))
        name_entry.insert("1.0", current_category)
        name_entry.focus()
        self.setup_context_menu_for_widget(name_entry)
        
        # Кнопки действий
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill=ctk.X, pady=(10, 0))
        
        def on_rename():
            new_name = name_entry.get("1.0", ctk.END).strip()
            if not new_name:
                self.show_status_message("✗ Введите название")
                return
            
            if new_name == current_category:
                self.edit_category_dialog_open = False
                dialog.destroy()
                return
            
            if self.template_manager.rename_category(current_category, new_name):
                self.category_header.update_categories(self.template_manager.get_categories())
                self.category_header.set_selected_category(new_name)
                self.force_update_templates_display()
                self.show_status_message("✓ Категория переименована")
                self.edit_category_dialog_open = False
                dialog.destroy()
            else:
                self.show_status_message("✗ Ошибка переименования")
        
        def on_delete():
            self.edit_category_dialog_open = False
            dialog.destroy()
            # Подтверждение удаления
            confirm_dialog = self.create_custom_dialog("Подтверждение", 400, 195)
            
            confirm_frame = ctk.CTkFrame(confirm_dialog.content_frame, fg_color="#1a1a1a")
            confirm_frame.pack(fill=ctk.BOTH, expand=True, padx=15, pady=15)
            
            ctk.CTkLabel(
                confirm_frame,
                text=f"Удалить категорию '{current_category}'?\nВсе шаблоны будут удалены.",
                text_color="white",
                font=("Segoe UI", 12)
            ).pack(pady=20)
            
            btn_confirm_frame = ctk.CTkFrame(confirm_frame, fg_color="transparent")
            btn_confirm_frame.pack(pady=10)
            
            def confirm_delete():
                if self.template_manager.delete_category(current_category):
                    categories = self.template_manager.get_categories()
                    self.category_header.update_categories(categories)
                    
                    if categories:
                        self.category_header.set_selected_category(categories[0])
                    
                    self.force_update_templates_display()
                    self.show_status_message("✓ Категория удалена")
                    self.edit_category_dialog_open = False
                    confirm_dialog.destroy()
                else:
                    self.show_status_message("✗ Ошибка удаления")
                    confirm_dialog.destroy()
            
            ctk.CTkButton(btn_confirm_frame, text="Да", command=confirm_delete, width=100).pack(side=ctk.LEFT, padx=5)
            ctk.CTkButton(btn_confirm_frame, text="Нет", command=confirm_dialog.destroy, width=100).pack(side=ctk.LEFT, padx=5)
        
        def on_cancel():
            self.edit_category_dialog_open = False
            dialog.destroy()
        
        # Кнопка переименования
        ctk.CTkButton(
            btn_frame,
            text="🔤 Переименовать",
            command=on_rename,
            width=SIZES.BUTTON_WIDTH_LARGE,
            font=FONTS.BUTTON_EMOJI
        ).pack(side=ctk.LEFT, padx=SIZES.PADDING_SMALL)
        
        # Кнопка удаления
        ctk.CTkButton(
            btn_frame,
            text=f"{EMOJI.DELETE} Удалить",
            command=on_delete,
            fg_color=COLORS.ACCENT_RED,
            hover_color=COLORS.ACCENT_RED_HOVER,
            width=SIZES.BUTTON_WIDTH_LARGE,
            font=FONTS.BUTTON_EMOJI
        ).pack(side=ctk.LEFT, padx=SIZES.PADDING_SMALL)
        
        # Кнопка отмены
        ctk.CTkButton(
            btn_frame,
            text="Отмена",
            command=on_cancel,
            width=SIZES.BUTTON_WIDTH_SMALL
        ).pack(side=ctk.LEFT, padx=SIZES.PADDING_SMALL)
        
        # Обработка горячих клавиш
        dialog.bind('<Return>', lambda e: on_rename())
        dialog.bind('<Escape>', lambda e: on_cancel())
    
    def add_template(self) -> None:
        """Добавление нового шаблона в текущую категорию"""
        # Проверка: если диалог уже открыт, не создавать новый
        if self.add_template_dialog_open:
            return
        
        current_category = self.category_header.get_selected_category()
        if not current_category:
            self.show_status_message("⚠ Сначала выберите категорию")
            return
        
        self.add_template_dialog_open = True
        
        # Обработчик закрытия окна
        def on_close():
            self.add_template_dialog_open = False
        
        # Создаем кастомный диалог для добавления шаблона
        dialog = self.create_custom_dialog("Добавить новый шаблон", 750, 700, on_close_callback=on_close)
        
        # Убираем старый обработчик WM_DELETE_WINDOW
        dialog.protocol("WM_DELETE_WINDOW", on_close)
        
        # Основной фрейм диалога
        main_frame = ctk.CTkFrame(dialog.content_frame, fg_color="#1a1a1a")
        main_frame.pack(fill=ctk.BOTH, expand=True, padx=15, pady=15)
        
        # Заголовок
        title_label = ctk.CTkLabel(
            main_frame,
            text=f"Добавить шаблон в категорию '{current_category}'",
            font=("Segoe UI", 14, "bold"),
            text_color="white"
        )
        title_label.pack(anchor="w", pady=(0, 15))
        
        # Поле для названия шаблона
        ctk.CTkLabel(main_frame, text="Название шаблона:", text_color="white").pack(anchor="w", pady=(10, 3))
        
        title_var = ctk.StringVar()
        title_entry = ctk.CTkTextbox(
            main_frame,
            height=2,
            font=("Segoe UI Emoji", 12),
            text_color="white",
            fg_color="#2b2b2b",
            border_color="#404040",
            border_width=1
        )
        title_entry.pack(fill=ctk.X, pady=(0, 15))
        title_entry.focus()
        self.setup_context_menu_for_widget(title_entry)
        
        # Поле для текста шаблона
        ctk.CTkLabel(main_frame, text="Текст шаблона:", text_color="white").pack(anchor="w", pady=(10, 3))
        
        text_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        text_frame.pack(fill=ctk.BOTH, expand=True, pady=(0, 15))
        
        # Текстовое поле для содержимого шаблона
        text_widget = ctk.CTkTextbox(
            text_frame,
            height=18,
            width=70,
            font=("Segoe UI", 12)
        )
        text_widget.pack(fill=ctk.BOTH, expand=True)
        self.setup_context_menu_for_widget(text_widget)
        
        # Кнопки действий
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill=ctk.X, pady=(10, 0), anchor="e")
        
        def on_save():
            template_title = title_entry.get("1.0", ctk.END).strip()
            template_text = text_widget.get("1.0", ctk.END).strip()
            
            if not template_title:
                self.show_status_message("✗ Введите название")
                return
            
            if not template_text:
                self.show_status_message("✗ Введите текст")
                return
            
            if self.template_manager.add_template(current_category, template_title, template_text):
                # ОПТИМИЗАЦИЯ: Обновляем индекс поиска
                self.search_indexer.build_index(self.template_manager)
                self.show_status_message("✓ Шаблон добавлен")
                self.force_update_templates_display()
                self.add_template_dialog_open = False
                dialog.destroy()
            else:
                self.show_status_message("✗ Ошибка добавления")
        
        def on_cancel():
            self.add_template_dialog_open = False
            dialog.destroy()
        
        save_img = EmojiIconButton.get_ctk_image("💾", size=16)
        ctk.CTkButton(
            btn_frame,
            text="Сохранить",
            image=save_img,
            compound="left",
            command=on_save,
            width=150
        ).pack(side=ctk.LEFT, padx=5)
        
        ctk.CTkButton(
            btn_frame,
            text="Отмена",
            command=on_cancel,
            width=100
        ).pack(side=ctk.LEFT, padx=5)
        
        # Обработка горячих клавиш
        dialog.bind('<Escape>', lambda e: on_cancel())
    
    def show_modern_dialog(self, title: str, prompt: str, initial_value: str = "") -> str:
        """Современный диалог ввода"""
        dialog = self.create_custom_dialog(title, 400, 215)
        
        # Содержимое диалога
        main_frame = ctk.CTkFrame(dialog.content_frame, fg_color="#1a1a1a")
        main_frame.pack(fill=ctk.BOTH, expand=True, padx=15, pady=15)
        
        ctk.CTkLabel(main_frame, text=prompt, text_color="white").pack(pady=15)
        
        # Используем Textbox вместо Entry для поддержки эмодзи
        text_widget = ctk.CTkTextbox(
            main_frame, 
            height=2,
            font=("Segoe UI Emoji", 12),
            text_color="white",
            fg_color="#2b2b2b",
            border_color="#404040",
            border_width=1
        )
        text_widget.pack(fill=ctk.X, pady=5)
        text_widget.insert("1.0", initial_value)
        text_widget.focus()
        self.setup_context_menu_for_widget(text_widget)
        
        result = []
        
        def on_ok():
            result.append(text_widget.get("1.0", ctk.END).strip())
            dialog.destroy()
        
        def on_cancel():
            result.append(None)
            dialog.destroy()
        
        # Обработчик закрытия окна (в том числе крестик)
        def on_dialog_close():
            self.add_category_dialog_open = False
            if not result:  # Если результат не добавлен (закрыто крестиком)
                on_cancel()
        
        dialog.protocol("WM_DELETE_WINDOW", on_dialog_close)
        
        # Кнопки
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(pady=15)
        
        ctk.CTkButton(btn_frame, text="OK", command=on_ok, width=100).pack(side=ctk.LEFT, padx=5)
        ctk.CTkButton(btn_frame, text="Отмена", command=on_cancel, width=100).pack(side=ctk.LEFT, padx=5)
        
        # Обработка Enter и Escape
        dialog.bind('<Return>', lambda e: on_ok())
        dialog.bind('<Escape>', lambda e: on_cancel())
        
        self.root.wait_window(dialog)
        return result[0] if result else None
    
    def update_templates_display(self) -> None:
        """Обновление отображения шаблонов"""
        current_category = self.category_header.get_selected_category()
        
        # Сохраняем текущее состояние
        self._last_displayed_category = current_category
        self._last_search_query = self.search_query
        
        # Очистка текущего отображения
        for widget in self.templates_frame.winfo_children():
            widget.destroy()
        
        if not current_category:
            # Плейсхолдер при отсутствии выбранной категории
            placeholder = ctk.CTkLabel(
                self.templates_frame, 
                text="👆 Выберите категорию для просмотра шаблонов", 
                text_color="#a0a0a0",
                font=("Segoe UI", 14)
            )
            placeholder.pack(expand=True, pady=100)
            return
        
        # Получаем ВСЕ шаблоны из кэша
        templates = self.template_manager.get_templates_cached(current_category)
        
        # Фильтруем если есть поисковый запрос
        if self.search_query:
            templates = [t for t in templates 
                        if self.search_query in t.get('title', '').lower() 
                        or self.search_query in t.get('text', '').lower()]
        
        if not templates:
            # Плейсхолдер для пустой категории
            if self.search_query:
                empty_label = ctk.CTkLabel(
                    self.templates_frame, 
                    text=f'Ничего не найдено: "{self.search_query}"', 
                    text_color="#a0a0a0",
                    font=("Segoe UI", 12)
                )
            else:
                empty_label = ctk.CTkLabel(
                    self.templates_frame, 
                    text="В этой категории пока нет шаблонов", 
                    text_color="#a0a0a0",
                    font=("Segoe UI", 12)
                )
            empty_label.pack(expand=True, pady=100)
            return
        
        # Создание контейнера для содержимого
        content_container = ctk.CTkFrame(self.templates_frame, fg_color="transparent")
        content_container.pack(fill=ctk.BOTH, expand=True)
        
        # Создание современной прокручиваемой области
        self.create_modern_scrollable_frame(templates, content_container, current_category)
    
    def force_update_templates_display(self) -> None:
        """Принудительное обновление отображения"""
        self._last_displayed_category = None
        self._last_search_query = None
        self.update_templates_display()
    
    def create_modern_scrollable_frame(self, templates: list, parent_container, current_category: str) -> None:
        """Создание современной прокручиваемой области для шаблонов"""
        # ОПТИМИЗАЦИЯ: Поиск уже выполнен в update_templates_display,
        # если используются search_results, то фильтрация уже сделана
        filtered_templates = templates
        
        # Основной контейнер
        container = ctk.CTkFrame(parent_container, fg_color="transparent")
        container.pack(fill=ctk.BOTH, expand=True)
        
        # Если нет результатов поиска
        if not filtered_templates and self.search_query:
            no_results = ctk.CTkLabel(
                container,
                text=f'Шаблоны не найдены: "{self.search_query}"',
                text_color="#a0a0a0",
                font=("Segoe UI", 12)
            )
            no_results.pack(expand=True, pady=100)
            return
        
        # Canvas и скроллбар
        canvas = ctk.CTkCanvas(
            container, 
            bg="#1a1a1a",
            highlightthickness=0
        )
        
        scrollbar = ctk.CTkScrollbar(
            container, 
            orientation="vertical", 
            command=canvas.yview
        )
        
        scrollable_frame = ctk.CTkFrame(canvas, fg_color="#1a1a1a")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        # Получаем доступную ширину
        available_width = self.templates_frame.winfo_width()
        if available_width <= 1:
            available_width = 900  # Значение по умолчанию
        
        canvas_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=available_width - 20)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Автоматическое изменение ширины контента
        def configure_canvas(event):
            canvas.itemconfig(canvas_id, width=event.width - 20)
        
        canvas.bind("<Configure>", configure_canvas)
        
        # Функция для скролла мышью по всей области
        def on_mousewheel(event):
            """Обработка скролла мышью по всему canvas"""
            # Определяем направление скролла
            if event.num == 5 or event.delta < 0:
                canvas.yview_scroll(3, "units")
            elif event.num == 4 or event.delta > 0:
                canvas.yview_scroll(-3, "units")
        
        # Привязываем скролл к canvas и всем его дочерним элементам
        canvas.bind("<MouseWheel>", on_mousewheel)
        canvas.bind("<Button-4>", on_mousewheel)
        canvas.bind("<Button-5>", on_mousewheel)
        scrollable_frame.bind("<MouseWheel>", on_mousewheel)
        scrollable_frame.bind("<Button-4>", on_mousewheel)
        scrollable_frame.bind("<Button-5>", on_mousewheel)
        
        # Отображение каждого шаблона
        templates_full = self.template_manager.get_templates_cached(current_category)
        for idx, template in enumerate(filtered_templates):
            # Найди реальный индекс в полном списке
            real_idx = None
            for full_idx, full_tpl in enumerate(templates_full):
                if full_tpl.get('title') == template.get('title'):
                    real_idx = full_idx
                    break
            
            TemplateWidget(
                parent=scrollable_frame,
                template=template,
                template_index=real_idx,
                copy_callback=self.copy_template_text,
                edit_callback=self.edit_template_with_index,
                pin_callback=self.toggle_pin_template_by_name,
                stats_callback=self.show_template_stats
            )
        
        # Упаковка элементов
        canvas.pack(side="left", fill="both", expand=True, padx=(0, 5))
        scrollbar.pack(side="right", fill="y")
    
    def display_top_used_templates(self, parent_container, category: str) -> None:
        """Отображение топ 3 используемых шаблонов"""
        top_templates = self.template_manager.get_top_used_templates(category, limit=3)
        
        if not top_templates or sum(t.get('stats', {}).get('usage_count', 0) for t in top_templates) == 0:
            # Не показываем, если нет использованных шаблонов
            return
        
        # Секция топ используемых
        top_frame = ctk.CTkFrame(parent_container, fg_color=COLORS.BG_MEDIUM, corner_radius=10)
        top_frame.pack(fill=ctk.X, pady=(0, 15), padx=0)
        
        # Заголовок
        header_frame = ctk.CTkFrame(top_frame, fg_color="transparent")
        header_frame.pack(fill=ctk.X, padx=15, pady=(10, 5))
        
        header_label = ctk.CTkLabel(
            header_frame,
            text="🏆 Топ используемых шаблонов",
            font=("Segoe UI", 12, "bold"),
            text_color="#1E90FF"
        )
        header_label.pack(anchor="w")
        
        # Список топ шаблонов
        for idx, template in enumerate(top_templates, 1):
            usage_count = template.get('stats', {}).get('usage_count', 0)
            if usage_count == 0:
                continue
            
            item_frame = ctk.CTkFrame(top_frame, fg_color="transparent")
            item_frame.pack(fill=ctk.X, padx=15, pady=3)
            
            # Ранг
            rank_label = ctk.CTkLabel(
                item_frame,
                text=f"#{idx}",
                font=("Segoe UI", 11, "bold"),
                text_color="#FFD700",
                width=30
            )
            rank_label.pack(side=ctk.LEFT, padx=(0, 10))
            
            # Название и количество использований
            info_label = ctk.CTkLabel(
                item_frame,
                text=f"{template.get('title', 'Шаблон')} ({usage_count}x)",
                font=("Segoe UI", 11),
                text_color="#FFFFFF",
                anchor="w"
            )
            info_label.pack(side=ctk.LEFT, fill=ctk.X, expand=True)
    
    def copy_template_text(self, template: dict) -> None:
        """Копирование текста шаблона в буфер обмена и увеличение счётчика использования"""
        text = template.get('text', '')
        if copy_to_clipboard(self.root, text):
            # Увеличиваем счётчик использования (без перерисовки)
            current_category = self.category_header.get_selected_category()
            if current_category:
                self.template_manager.increment_usage(current_category, template)
            self.show_status_message("✓ Текст скопирован")
        else:
            self.show_status_message("✗ Ошибка копирования")
    
    def toggle_pin_template(self, template_index: int) -> None:
        """Переключение закрепления шаблона (по индексу - DEPRECATED)"""
        current_category = self.category_header.get_selected_category()
        if not current_category:
            return
        
        if self.template_manager.toggle_pin_template(current_category, template_index):
            self.force_update_templates_display()
        else:
            self.show_status_message("✗ Ошибка закрепления")
    
    def toggle_pin_template_by_name(self, template: dict) -> None:
        """Переключение закрепления шаблона (по названию)"""
        current_category = self.category_header.get_selected_category()
        if not current_category:
            return
        
        if self.template_manager.toggle_pin_template_by_name(current_category, template):
            # Получаем новое состояние шаблона (ПОСЛЕ переключения)
            templates = self.template_manager.get_templates(current_category)
            for tpl in templates:
                if tpl.get('title') == template.get('title'):
                    is_pinned = tpl.get('pinned', False)
                    break
            else:
                is_pinned = False
            
            # Обновляем отображение после изменения закрепления
            self.force_update_templates_display()
            
            # Показываем сообщение с новым состоянием
            if is_pinned:
                self.show_status_message("⭐ Шаблон закреплён")
            else:
                self.show_status_message("☆ Закрепление снято")
        else:
            self.show_status_message("✗ Ошибка закрепления")
    
    def edit_template_with_index(self, template: dict, template_index: int = None) -> None:
        """Редактирование шаблона с индексом или по названию"""
        current_category = self.category_header.get_selected_category()
        if not current_category:
            return
        
        # Если индекс не передан, ищем по названию (для обратной совместимости)
        if template_index is None:
            templates = self.template_manager.get_templates(current_category)
            for idx, tpl in enumerate(templates):
                if tpl.get('title') == template.get('title'):
                    template_index = idx
                    break
        
        if template_index is None:
            self.show_status_message("✗ Шаблон не найден")
            return
        
        # Вызываем оригинальный метод редактирования
        self.edit_template(template_index)
    
    def edit_template(self, template_index: int) -> None:
        """Редактирование выбранного шаблона"""
        # Проверка: если диалог уже открыт, не создавать новый
        if self.edit_template_dialog_open:
            return
        
        current_category = self.category_header.get_selected_category()
        if not current_category:
            self.show_status_message("⚠ Сначала выберите категорию")
            return
        
        templates = self.template_manager.get_templates(current_category)
        if not templates or template_index >= len(templates) or template_index < 0:
            self.show_status_message("⚠ Ошибка: шаблон не найден")
            return
        
        self.edit_template_dialog_open = True
        
        template = templates[template_index]
        
        # Обработчик закрытия окна
        def on_close():
            self.edit_template_dialog_open = False
        
        # Создаем кастомный диалог для редактирования шаблона
        dialog = self.create_custom_dialog("Редактировать шаблон", 750, 700, on_close_callback=on_close)
        
        # Убираем старый обработчик WM_DELETE_WINDOW
        dialog.protocol("WM_DELETE_WINDOW", on_close)
        
        # Основной фрейм диалога
        main_frame = ctk.CTkFrame(dialog.content_frame, fg_color="#1a1a1a")
        main_frame.pack(fill=ctk.BOTH, expand=True, padx=15, pady=15)
        
        # Заголовок
        title_label = ctk.CTkLabel(
            main_frame,
            text=f"Редактировать шаблон в категории '{current_category}'",
            font=("Segoe UI", 14, "bold"),
            text_color="white"
        )
        title_label.pack(anchor="w", pady=(0, 15))
        
        # Поле для названия шаблона
        ctk.CTkLabel(main_frame, text="Название шаблона:", text_color="white").pack(anchor="w", pady=(10, 3))
        
        title_entry = ctk.CTkTextbox(
            main_frame,
            height=2,
            font=("Segoe UI Emoji", 12),
            text_color="white",
            fg_color="#2b2b2b",
            border_color="#404040",
            border_width=1
        )
        title_entry.pack(fill=ctk.X, pady=(0, 15))
        title_entry.insert("1.0", template['title'])
        self.setup_context_menu_for_widget(title_entry)
        
        # Поле для текста шаблона
        ctk.CTkLabel(main_frame, text="Текст шаблона:", text_color="white").pack(anchor="w", pady=(10, 3))
        
        text_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        text_frame.pack(fill=ctk.BOTH, expand=True, pady=(0, 15))
        
        # Текстовое поле для содержимого шаблона
        text_widget = ctk.CTkTextbox(
            text_frame,
            height=18,
            width=70,
            font=("Segoe UI", 12)
        )
        text_widget.insert("1.0", template['text'])
        text_widget.pack(fill=ctk.BOTH, expand=True)
        self.setup_context_menu_for_widget(text_widget)
        
        # Кнопки действий
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill=ctk.X, pady=(10, 0), anchor="e")
        
        def on_save():
            template_title = title_entry.get("1.0", ctk.END).strip()
            template_text = text_widget.get("1.0", ctk.END).strip()
            
            if not template_title:
                self.show_status_message("✗ Введите название")
                return
            
            if not template_text:
                self.show_status_message("✗ Введите текст")
                return
            
            if self.template_manager.edit_template(current_category, template_index, template_title, template_text):
                # ОПТИМИЗАЦИЯ: Обновляем индекс поиска
                self.search_indexer.build_index(self.template_manager)
                self.show_status_message("✓ Шаблон обновлен")
                self.force_update_templates_display()
                self.edit_template_dialog_open = False
                dialog.destroy()
            else:
                self.show_status_message("✗ Ошибка сохранения")
        
        def on_delete():
            self.edit_template_dialog_open = False
            dialog.destroy()
            # Подтверждение удаления
            confirm_dialog = self.create_custom_dialog("Подтверждение", 350, 175)
            
            confirm_frame = ctk.CTkFrame(confirm_dialog.content_frame, fg_color="#1a1a1a")
            confirm_frame.pack(fill=ctk.BOTH, expand=True, padx=15, pady=15)
            
            ctk.CTkLabel(
                confirm_frame,
                text="Удалить этот шаблон?",
                text_color="white",
                font=("Segoe UI", 12)
            ).pack(pady=20)
            
            btn_confirm_frame = ctk.CTkFrame(confirm_frame, fg_color="transparent")
            btn_confirm_frame.pack(pady=10)
            
            def confirm_delete():
                if self.template_manager.delete_template(current_category, template_index):
                    # ОПТИМИЗАЦИЯ: Обновляем индекс поиска
                    self.search_indexer.build_index(self.template_manager)
                    self.show_status_message("✓ Шаблон удален")
                    self.force_update_templates_display()
                    confirm_dialog.destroy()
                else:
                    self.show_status_message("✗ Ошибка удаления")
                    confirm_dialog.destroy()
            
            ctk.CTkButton(btn_confirm_frame, text="Да", command=confirm_delete, width=100).pack(side=ctk.LEFT, padx=5)
            ctk.CTkButton(btn_confirm_frame, text="Нет", command=confirm_dialog.destroy, width=100).pack(side=ctk.LEFT, padx=5)
        
        def on_cancel():
            self.edit_template_dialog_open = False
            dialog.destroy()
        
        save_img2 = EmojiIconButton.get_ctk_image("💾", size=16)
        ctk.CTkButton(
            btn_frame,
            text="Сохранить",
            image=save_img2,
            compound="left",
            command=on_save,
            width=150
        ).pack(side=ctk.LEFT, padx=5)
        
        delete_img = EmojiIconButton.get_ctk_image("🗑️", size=16)
        ctk.CTkButton(
            btn_frame,
            text="Удалить",
            image=delete_img,
            compound="left",
            command=on_delete,
            fg_color="#d32f2f",
            hover_color="#b71c1c",
            width=150
        ).pack(side=ctk.LEFT, padx=5)
        
        ctk.CTkButton(
            btn_frame,
            text="Отмена",
            command=on_cancel,
            width=100
        ).pack(side=ctk.LEFT, padx=5)
    
    def check_updates_on_startup(self):
        """Проверить обновления в отдельном потоке"""
        thread = threading.Thread(target=self._check_updates_background, daemon=True)
        thread.start()
    
    def _check_updates_background(self):
        """Проверить обновления в фоновом потоке"""
        try:
            has_update, remote_version, download_url = AppUpdater.check_for_updates()
            
            if has_update:
                # Вызываем диалог в главном потоке
                self.root.after(0, lambda: self.show_update_dialog(remote_version, download_url))
        except Exception as e:
            print(f"Ошибка при проверке обновлений: {e}")
    
    def show_update_dialog(self, remote_version, download_url):
        """Показать диалог об обновлении"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Доступно обновление")
        dialog.geometry("450x250")
        dialog.resizable(False, False)
        
        # Устанавливаем иконку
        try:
            icon_paths = PATHS.get_icon_paths()
            for path in icon_paths:
                if path and path.exists():
                    dialog.iconbitmap(str(path))
                    break
        except:
            pass
        
        # Центрируем диалог
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (450 // 2)
        y = (dialog.winfo_screenheight() // 2) - (250 // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Устанавливаем поверх всех окон
        dialog.attributes("-topmost", True)
        dialog.lift()
        dialog.focus_force()
        
        # Заголовок
        title_label = ctk.CTkLabel(
            dialog,
            text="🎉 Доступно обновление!",
            font=("Segoe UI", 18, "bold")
        )
        title_label.pack(pady=(20, 10))
        
        # Информация о версии
        info_label = ctk.CTkLabel(
            dialog,
            text=f"Новая версия: {remote_version}\n\nОбновить приложение сейчас?",
            font=("Segoe UI", 13)
        )
        info_label.pack(pady=10)
        
        # Прогресс бар (изначально скрыт)
        progress_label = ctk.CTkLabel(
            dialog,
            text="Загрузка обновления...",
            font=("Segoe UI", 11)
        )
        
        progress_bar = ctk.CTkProgressBar(dialog, width=350)
        progress_bar.set(0)
        
        def update_now():
            # Скрываем кнопки, показываем прогресс
            btn_frame.pack_forget()
            progress_label.pack(pady=5)
            progress_bar.pack(pady=10)
            
            # Запускаем загрузку в отдельном потоке
            thread = threading.Thread(
                target=self._download_and_install,
                args=(download_url, progress_bar, dialog),
                daemon=True
            )
            thread.start()
        
        def skip():
            dialog.destroy()
        
        # Кнопки
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(pady=20)
        
        update_btn = ctk.CTkButton(
            btn_frame,
            text="✅ Обновить",
            command=update_now,
            width=150,
            height=35,
            font=("Segoe UI", 12, "bold"),
            fg_color="#4CAF50",
            hover_color="#45a049"
        )
        update_btn.pack(side="left", padx=10)
        
        skip_btn = ctk.CTkButton(
            btn_frame,
            text="❌ Пропустить",
            command=skip,
            width=150,
            height=35,
            font=("Segoe UI", 12),
            fg_color="#757575",
            hover_color="#616161"
        )
        skip_btn.pack(side="left", padx=10)
    
    def _download_and_install(self, download_url, progress_bar, dialog):
        """Скачать и установить обновление"""
        def update_progress(value):
            # Обновляем прогресс в главном потоке
            self.root.after(0, lambda: progress_bar.set(value / 100))
        
        # Скачиваем обновление
        success, update_path = AppUpdater.download_update(download_url, update_progress)
        
        if success:
            # Закрываем диалог
            self.root.after(0, dialog.destroy)
            # Устанавливаем обновление
            self.root.after(100, lambda: AppUpdater.install_update(self.root))
        else:
            # Показываем ошибку
            self.root.after(0, lambda: self._show_update_error(dialog))
    
    def show_template_stats(self, template: dict) -> None:
        """Показать статистику использования шаблона"""
        current_category = self.category_header.get_selected_category()
        if not current_category:
            return
        
        # Получаем статистику
        stats = self.template_manager.get_template_stats(current_category, template)
        usage_count = stats.get('usage_count', 0) if stats else 0
        
        # Создаём диалоговое окно
        stats_dialog = ctk.CTkToplevel(self.root)
        stats_dialog.title("Статистика использования")
        stats_dialog.geometry("400x250")
        
        # Устанавливаем иконку
        try:
            icon_paths = PATHS.get_icon_paths()
            for path in icon_paths:
                if path and path.exists():
                    stats_dialog.iconbitmap(str(path))
                    break
        except:
            pass
        
        stats_dialog.attributes("-topmost", True)
        stats_dialog.resizable(False, False)
        
        # Основной фрейм
        main_frame = ctk.CTkFrame(stats_dialog, fg_color="transparent")
        main_frame.pack(fill=ctk.BOTH, expand=True, padx=20, pady=20)
        
        # Название шаблона
        title_label = ctk.CTkLabel(
            main_frame,
            text=template.get('title', 'Шаблон'),
            font=("Segoe UI", 14, "bold"),
            text_color="#FFFFFF"
        )
        title_label.pack(anchor="w", pady=(0, 15))
        
        # Статистика
        stats_text = f"👁️ Использован {usage_count} раз"
        stats_label = ctk.CTkLabel(
            main_frame,
            text=stats_text,
            font=("Segoe UI", 13),
            text_color="#1E90FF"
        )
        stats_label.pack(anchor="w", pady=10)
        
        # Кнопка закрытия
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill=ctk.X, pady=(20, 0))
        
        close_btn = ctk.CTkButton(
            btn_frame,
            text="Закрыть",
            command=stats_dialog.destroy,
            width=100,
            height=32
        )
        close_btn.pack(side=ctk.RIGHT)
        
        # Горячие клавиши
        stats_dialog.bind('<Escape>', lambda e: stats_dialog.destroy())
        stats_dialog.bind('<Return>', lambda e: stats_dialog.destroy())
        
        # Центрируем окно
        stats_dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (stats_dialog.winfo_width() // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (stats_dialog.winfo_height() // 2)
        stats_dialog.geometry(f"+{x}+{y}")
    
    def _show_update_error(self, parent_dialog):
        """Показать ошибку обновления"""
        parent_dialog.destroy()
        
        error_dialog = ctk.CTkToplevel(self.root)
        error_dialog.title("Ошибка обновления")
        error_dialog.geometry("400x150")
        
        # Устанавливаем иконку
        try:
            icon_paths = PATHS.get_icon_paths()
            for path in icon_paths:
                if path and path.exists():
                    error_dialog.iconbitmap(str(path))
                    break
        except:
            pass
        
        error_dialog.attributes("-topmost", True)
        
        label = ctk.CTkLabel(
            error_dialog,
            text="❌ Не удалось загрузить обновление\n\nПопробуйте позже",
            font=("Segoe UI", 13)
        )
        label.pack(pady=30)
        
        ok_btn = ctk.CTkButton(
            error_dialog,
            text="OK",
            command=error_dialog.destroy,
            width=100
        )
        ok_btn.pack(pady=10)
        
        # Обработка горячих клавиш
        error_dialog.bind('<Escape>', lambda e: error_dialog.destroy())
