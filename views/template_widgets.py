"""
Виджеты для отображения шаблонов и категорий
"""
import customtkinter as ctk
from typing import Callable
from config.constants import COLORS, FONTS, SIZES
from config.settings import EMOJI
from utils.icon_generator import EmojiIconButton


class ClickableComboBox(ctk.CTkComboBox):
    """
    Расширенный ComboBox, который открывается по клику на основное поле
    
    Улучшает UX, позволяя открывать выпадающий список кликом по всему виджету,
    а не только по стрелке.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Привязываем события клика на все элементы комбобокса
        self.bind('<Button-1>', self._on_click, add=True)
        
        # Настраиваем стиль выпадающего меню после инициализации
        self.after(100, self._configure_dropdown_style)
    
    def _configure_dropdown_style(self):
        """Настройка стиля выпадающего меню"""
        try:
            if hasattr(self, '_dropdown_menu') and self._dropdown_menu:
                dropdown = self._dropdown_menu
                
                # Получаем родительское окно (Toplevel)
                parent_window = None
                widget = dropdown
                while widget:
                    if hasattr(widget, 'winfo_toplevel'):
                        top = widget.winfo_toplevel()
                        if top != self.winfo_toplevel():
                            parent_window = top
                            break
                    if hasattr(widget, 'master'):
                        widget = widget.master
                    else:
                        break
                
                # Убираем рамки у родительского окна
                if parent_window:
                    try:
                        parent_window.overrideredirect(True)
                        parent_window.wm_attributes('-topmost', True)
                        # Настраиваем фон окна
                        parent_window.configure(bg='#2b2b2b')
                    except:
                        pass
                
                # Настраиваем само меню
                try:
                    dropdown.configure(
                        fg_color=COLORS.BG_MEDIUM,
                        corner_radius=SIZES.CORNER_RADIUS_MEDIUM,
                        border_width=1,
                        border_color=COLORS.BORDER_DEFAULT
                    )
                except:
                    pass
        except Exception:
            pass
    
    def _on_click(self, event):
        """Открываем выпадающий список при клике"""
        # Проверяем, есть ли выпадающий список и открыт ли он
        try:
            # Если список уже открыт, ничего не делаем
            if hasattr(self, '_dropdown_menu') and self._dropdown_menu.winfo_exists():
                if self._dropdown_menu.winfo_viewable():
                    self._dropdown_menu.close()
                    return
            # Открываем список
            self._open_dropdown_menu()
            # Применяем стиль после открытия
            self.after(10, self._configure_dropdown_style)
        except Exception:
            pass
    
    def _open_dropdown_menu(self):
        """Открыть выпадающий список"""
        try:
            # Получаем координаты и размеры
            x = self.winfo_rootx()
            y = self.winfo_rooty() + self.winfo_height()
            width = self.winfo_width()
            
            # Пытаемся вызвать приватный метод открытия
            if hasattr(self, '_dropdown_menu'):
                self._dropdown_menu.open(x, y)
            elif hasattr(self, '_open_dropdown'):
                self._open_dropdown()
        except Exception:
            pass

class TemplateWidget:
    """
    Виджет для отображения одного шаблона с возможностью копирования и редактирования
    
    Attributes:
        parent: Родительский виджет
        template (dict): Данные шаблона (title, text, pinned, stats)
        template_index (int): Индекс шаблона в списке
        copy_callback (Callable): Функция для копирования текста
        edit_callback (Callable): Функция для редактирования шаблона
        pin_callback (Callable): Функция для закрепления шаблона
        stats_callback (Callable): Функция для показа статистики
    """
    
    def __init__(self, parent, template: dict, template_index: int, 
                 copy_callback: Callable, edit_callback: Callable, pin_callback: Callable,
                 stats_callback: Callable = None):
        self.parent = parent
        self.template = template
        self.template_index = template_index
        self.copy_callback = copy_callback
        self.edit_callback = edit_callback
        self.pin_callback = pin_callback
        self.stats_callback = stats_callback
        
        self.create_widget()
    
    def create_widget(self) -> None:
        """Создание виджета шаблона с современным дизайном"""
        # Основной фрейм карточки
        self.frame = ctk.CTkFrame(
            self.parent, 
            fg_color=COLORS.BG_MEDIUM, 
            corner_radius=SIZES.CORNER_RADIUS_LARGE
        )
        self.frame.pack(fill=ctk.X, pady=8, padx=SIZES.PADDING_MEDIUM)
        
        # Заголовок карточки
        title_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        title_frame.pack(fill=ctk.X, pady=(SIZES.PADDING_LARGE, SIZES.PADDING_MEDIUM), 
                        padx=SIZES.PADDING_LARGE)
        
        # Название шаблона
        title_label = ctk.CTkLabel(
            title_frame, 
            text=self.template['title'], 
            font=FONTS.SUBTITLE,
            text_color=COLORS.TEXT_PRIMARY
        )
        title_label.pack(side=ctk.LEFT, expand=True, anchor="w")
        
        # Кнопка закрепления (звездочка)
        is_pinned = self.template.get('pinned', False)
        pin_emoji_char = "⭐" if is_pinned else "☆"
        pin_img = EmojiIconButton.get_ctk_image(pin_emoji_char, size=20)
        pin_btn = ctk.CTkButton(
            title_frame,
            text="",
            image=pin_img,
            command=lambda: self.pin_callback(self.template),
            width=32,
            height=32,
            corner_radius=SIZES.CORNER_RADIUS_SMALL,
            fg_color="transparent" if not is_pinned else COLORS.ACCENT_BLUE,
            hover_color=COLORS.HOVER_DARK
        )
        pin_btn.pack(side=ctk.RIGHT, padx=(SIZES.PADDING_SMALL, 0))
        
        # Кнопка копирования
        copy_img = EmojiIconButton.get_ctk_image("📋", size=16)
        copy_btn = ctk.CTkButton(
            title_frame,
            text="Копировать",
            image=copy_img,
            compound="left",
            command=lambda: self.copy_callback(self.template),
            width=140,
            height=SIZES.BUTTON_HEIGHT,
            corner_radius=SIZES.CORNER_RADIUS_SMALL
        )
        copy_btn.pack(side=ctk.RIGHT, padx=(SIZES.PADDING_SMALL, 0))
        
        # Кнопка редактирования
        edit_img = EmojiIconButton.get_ctk_image("📝", size=16)
        edit_btn = ctk.CTkButton(
            title_frame,
            text="Редактировать",
            image=edit_img,
            compound="left",
            command=lambda: self.edit_callback(self.template, self.template_index),
            width=150,
            height=SIZES.BUTTON_HEIGHT,
            corner_radius=SIZES.CORNER_RADIUS_SMALL
        )
        edit_btn.pack(side=ctk.RIGHT, padx=SIZES.PADDING_SMALL)
        
        # Текст шаблона
        text_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        text_frame.pack(fill=ctk.BOTH, expand=True, 
                       padx=SIZES.PADDING_LARGE, 
                       pady=(0, SIZES.PADDING_LARGE))
        
        self.text_widget = ctk.CTkTextbox(
            text_frame, 
            height=SIZES.TEMPLATE_DISPLAY_HEIGHT, 
            width=SIZES.TEXTBOX_WIDTH,
            fg_color=COLORS.BG_DARK,
            font=FONTS.TEXT
        )
        self.text_widget.insert("1.0", self.template['text'])
        self.text_widget.configure(state="disabled")
        self.text_widget.pack(fill=ctk.BOTH, expand=True)

class CategoryHeader:
    """
    Панель управления категориями шаблонов
    
    Attributes:
        parent: Родительский виджет
        on_category_select (Callable): Обработчик выбора категории
        on_category_type_select (Callable): Обработчик выбора типа категории
        on_add_category (Callable): Обработчик добавления категории
        on_edit_category (Callable): Обработчик редактирования категории
        on_add_template (Callable): Обработчик добавления шаблона
    """
    
    def __init__(self, parent, categories: list, category_types: list,
                 on_category_select: Callable,
                 on_category_type_select: Callable,
                 on_add_category: Callable,
                 on_edit_category: Callable,
                 on_add_template: Callable):
        self.parent = parent
        self.on_category_select = on_category_select
        self.on_category_type_select = on_category_type_select
        self.on_add_category = on_add_category
        self.on_edit_category = on_edit_category
        self.on_add_template = on_add_template
        
        self.create_widget(categories, category_types)
    
    def create_widget(self, categories: list, category_types: list) -> None:
        """Создание панели управления"""
        # Основной фрейм
        self.frame = ctk.CTkFrame(
            self.parent, 
            fg_color=COLORS.BG_MEDIUM, 
            corner_radius=SIZES.CORNER_RADIUS_LARGE
        )
        self.frame.pack(fill=ctk.X, pady=(0, SIZES.PADDING_MEDIUM), padx=SIZES.PADDING_MEDIUM)
        
        # Заголовок
        header_label = ctk.CTkLabel(
            self.frame, 
            text="Хелпер - управление шаблонами", 
            font=FONTS.HEADER,
            text_color=COLORS.TEXT_PRIMARY
        )
        header_label.pack(anchor="w", pady=(SIZES.PADDING_LARGE, SIZES.PADDING_LARGE), 
                         padx=SIZES.PADDING_LARGE)
        
        # Панель управления
        control_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        control_frame.pack(fill=ctk.X, padx=SIZES.PADDING_LARGE, 
                          pady=(0, SIZES.PADDING_LARGE))
        
        # Левая часть - выбор типа и категории
        self._create_selection_controls(control_frame, categories, category_types)
        
        # Правая часть - кнопки действий
        self._create_action_buttons(control_frame)
    
    def _create_selection_controls(self, parent, categories: list, category_types: list) -> None:
        """Создание элементов выбора типа и категории"""
        left_frame = ctk.CTkFrame(parent, fg_color="transparent")
        left_frame.pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True)
        
        # Выбор типа категорий
        ctk.CTkLabel(
            left_frame, 
            text="Тип:", 
            text_color=COLORS.TEXT_PRIMARY, 
            font=FONTS.BUTTON
        ).pack(side=ctk.LEFT, padx=(0, 8))
        
        self.type_var = ctk.StringVar()
        self.type_combo = ClickableComboBox(
            left_frame, 
            variable=self.type_var,
            values=category_types,
            state="readonly",
            font=FONTS.BUTTON,
            dropdown_fg_color=COLORS.BG_MEDIUM,
            dropdown_hover_color=COLORS.HOVER_DARK,
            dropdown_text_color=COLORS.TEXT_PRIMARY,
            button_color=COLORS.BG_LIGHT,
            button_hover_color=COLORS.HOVER_LIGHT,
            border_color=COLORS.BORDER_DEFAULT,
            fg_color=COLORS.BG_MEDIUM,
            text_color=COLORS.TEXT_PRIMARY,
            width=120
        )
        self.type_combo.pack(side=ctk.LEFT, padx=(0, SIZES.PADDING_XLARGE))
        self.type_combo.configure(command=lambda _: self.on_type_select())
        
        if category_types:
            self.type_combo.set(category_types[0])
        
        # Выбор категории
        ctk.CTkLabel(
            left_frame, 
            text="Категория:", 
            text_color=COLORS.TEXT_PRIMARY, 
            font=FONTS.BUTTON
        ).pack(side=ctk.LEFT, padx=(0, 8))
        
        self.category_var = ctk.StringVar()
        self.category_combo = ClickableComboBox(
            left_frame, 
            variable=self.category_var,
            values=categories,
            state="readonly",
            font=FONTS.TEXT,
            dropdown_fg_color=COLORS.BG_MEDIUM,
            dropdown_hover_color=COLORS.HOVER_DARK,
            dropdown_text_color=COLORS.TEXT_PRIMARY,
            button_color=COLORS.BG_LIGHT,
            button_hover_color=COLORS.HOVER_LIGHT,
            border_color=COLORS.BORDER_DEFAULT,
            fg_color=COLORS.BG_MEDIUM,
            text_color=COLORS.TEXT_PRIMARY
        )
        self.category_combo.pack(side=ctk.LEFT, fill=ctk.X, expand=True)
        self.category_combo.configure(command=lambda _: self.on_category_select_callback())
        
        if categories:
            self.category_combo.set(categories[0])
    
    def _create_action_buttons(self, parent) -> None:
        """Создание кнопок действий"""
        right_frame = ctk.CTkFrame(parent, fg_color="transparent")
        right_frame.pack(side=ctk.RIGHT, padx=(SIZES.PADDING_LARGE, 0))
        
        # Группа 1: Управление категориями
        category_group = ctk.CTkFrame(right_frame, fg_color="transparent")
        category_group.pack(side=ctk.LEFT, padx=(0, 15))
        
        # Кнопка добавления категории
        add_cat_img = EmojiIconButton.get_ctk_image("➕", size=16)
        ctk.CTkButton(
            category_group, 
            text="Добавить",
            image=add_cat_img,
            compound="left",
            command=self.on_add_category,
            width=SIZES.BUTTON_WIDTH_MEDIUM,
            height=SIZES.BUTTON_LARGE_HEIGHT,
            corner_radius=SIZES.CORNER_RADIUS_SMALL
        ).pack(side=ctk.LEFT, padx=3)
        
        # Кнопка редактирования категории
        edit_cat_img = EmojiIconButton.get_ctk_image("📝", size=16)
        ctk.CTkButton(
            category_group, 
            text="Редактировать", 
            image=edit_cat_img,
            compound="left",
            command=self.on_edit_category,
            width=SIZES.BUTTON_WIDTH_LARGE,
            height=SIZES.BUTTON_LARGE_HEIGHT,
            corner_radius=SIZES.CORNER_RADIUS_SMALL
        ).pack(side=ctk.LEFT, padx=3)
        
        # Разделитель
        separator = ctk.CTkLabel(
            right_frame,
            text="|",
            text_color="#666666",
            font=("Segoe UI", 18)
        )
        separator.pack(side=ctk.LEFT, padx=8)
        
        # Группа 2: Управление шаблонами
        template_group = ctk.CTkFrame(right_frame, fg_color="transparent")
        template_group.pack(side=ctk.LEFT)
        
        # Кнопка нового шаблона
        new_templ_img = EmojiIconButton.get_ctk_image("➕", size=16)
        ctk.CTkButton(
            template_group, 
            text="Новый шаблон", 
            image=new_templ_img,
            compound="left",
            command=self.on_add_template,
            width=SIZES.BUTTON_WIDTH_LARGE,
            height=SIZES.BUTTON_LARGE_HEIGHT,
            corner_radius=SIZES.CORNER_RADIUS_SMALL
        ).pack(side=ctk.LEFT, padx=3)
    
    def update_categories(self, categories: list) -> None:
        """Обновить список категорий"""
        self.category_combo.configure(values=categories)
        # Устанавливаем первую категорию, если она существует
        if categories:
            self.category_combo.set(categories[0])
        else:
            self.category_combo.set("")
    
    def get_selected_category(self) -> str:
        """Получить выбранную категорию"""
        return self.category_var.get()
    
    def set_selected_category(self, category: str) -> None:
        """Установить выбранную категорию"""
        self.category_var.set(category)
    
    def on_type_select(self):
        """Обработчик выбора типа категорий"""
        selected_type = self.type_var.get()
        self.on_category_type_select(selected_type)
    
    def on_category_select_callback(self):
        """Обработчик выбора категории"""
        self.on_category_select()