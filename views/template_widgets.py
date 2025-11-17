import customtkinter as ctk
from typing import Callable

# Стандартизированные размеры шрифтов для консистентности
FONT_TITLE = ("Segoe UI", 14, "bold")  # Заголовок окна
FONT_BUTTON_EMOJI = ("Segoe UI", 13)  # Кнопки с эмодзи
FONT_BUTTON = ("Segoe UI", 12)  # Обычные кнопки
FONT_LABEL = ("Segoe UI", 11)  # Подписи
FONT_SMALL = ("Segoe UI", 10)  # Маленький текст

class ClickableComboBox(ctk.CTkComboBox):
    """Расширенный ComboBox, который открывается по клику на основное поле"""
    
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
                        fg_color="#2b2b2b",
                        corner_radius=8,
                        border_width=1,
                        border_color="#404040"
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
    """Современный виджет для отображения одного шаблона"""
    
    def __init__(self, parent, template: dict, template_index: int, copy_callback: Callable, edit_callback: Callable):
        self.parent = parent
        self.template = template
        self.template_index = template_index
        self.copy_callback = copy_callback
        self.edit_callback = edit_callback
        
        self.create_widget()
    
    def create_widget(self) -> None:
        """Создание современного виджета шаблона"""
        # Основной фрейм карточки
        self.frame = ctk.CTkFrame(self.parent, fg_color="#2b2b2b", corner_radius=10)
        self.frame.pack(fill=ctk.X, pady=8, padx=10)
        
        # Заголовок карточки
        title_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        title_frame.pack(fill=ctk.X, pady=(15, 10), padx=15)
        
        title_label = ctk.CTkLabel(
            title_frame, 
            text=self.template['title'], 
            font=("Segoe UI Emoji", 14, "bold"),
            text_color="white"
        )
        title_label.pack(side=ctk.LEFT, expand=True, anchor="w")
        
        # Кнопка копирования
        copy_btn = ctk.CTkButton(
            title_frame,
            text="📋 Копировать",
            command=lambda: self.copy_callback(self.template['text']),
            width=120,
            height=32,
            corner_radius=6,
            font=("Segoe UI Emoji", 12)
        )
        copy_btn.pack(side=ctk.RIGHT, padx=(5, 0))
        
        # Кнопка редактирования
        edit_btn = ctk.CTkButton(
            title_frame,
            text="✏️ Редактировать",
            command=lambda: self.edit_callback(self.template_index),
            width=140,
            height=32,
            corner_radius=6,
            font=("Segoe UI Emoji", 12)
        )
        edit_btn.pack(side=ctk.RIGHT, padx=5)
        
        # Текст шаблона в современном стиле
        text_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        text_frame.pack(fill=ctk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        # Используем Textbox с современным стилем
        self.text_widget = ctk.CTkTextbox(
            text_frame, 
            height=150, 
            width=70,
            fg_color="#1a1a1a",
            font=("Segoe UI Emoji", 11)
        )
        self.text_widget.insert("1.0", self.template['text'])
        self.text_widget.configure(state="disabled")
        self.text_widget.pack(fill=ctk.BOTH, expand=True)

class CategoryHeader:
    """Современная верхняя панель с выбором категории"""
    
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
        """Создание современного виджета заголовка категории"""
        # Основной фрейм с цветным фоном
        self.frame = ctk.CTkFrame(self.parent, fg_color="#2b2b2b", corner_radius=10)
        self.frame.pack(fill=ctk.X, pady=(0, 10), padx=10)
        
        # Заголовок секции
        header_label = ctk.CTkLabel(
            self.frame, 
            text="Хелпер - управление шаблонами", 
            font=("Segoe UI", 18, "bold"),
            text_color="white"
        )
        header_label.pack(anchor="w", pady=(15, 15), padx=15)
        
        # Панель управления
        control_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        control_frame.pack(fill=ctk.X, padx=15, pady=(0, 15))
        
        # Левая часть - выбор типа категорий и категории
        left_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        left_frame.pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True)
        
        # Выбор типа категорий
        ctk.CTkLabel(left_frame, text="Тип:", text_color="white", font=("Segoe UI", 12)).pack(side=ctk.LEFT, padx=(0, 8))
        
        self.type_var = ctk.StringVar()
        self.type_combo = ClickableComboBox(
            left_frame, 
            variable=self.type_var,
            values=category_types,
            state="readonly",
            font=("Segoe UI", 12),
            dropdown_fg_color="#2b2b2b",
            dropdown_hover_color="#404040",
            dropdown_text_color="white",
            button_color="#404040",
            button_hover_color="#505050",
            border_color="#404040",
            fg_color="#2b2b2b",
            text_color="white",
            width=120
        )
        self.type_combo.pack(side=ctk.LEFT, padx=(0, 20))
        self.type_combo.configure(command=lambda _: self.on_type_select())
        
        # Инициализируем первый тип
        if category_types:
            self.type_combo.set(category_types[0])
        
        # Выбор категории
        ctk.CTkLabel(left_frame, text="Категория:", text_color="white", font=("Segoe UI", 12)).pack(side=ctk.LEFT, padx=(0, 8))
        
        # Используем кастомный комбобокс, который открывается по клику
        self.category_var = ctk.StringVar()
        self.category_combo = ClickableComboBox(
            left_frame, 
            variable=self.category_var,
            values=categories,
            state="readonly",
            font=("Segoe UI Emoji", 12),
            dropdown_fg_color="#2b2b2b",
            dropdown_hover_color="#404040",
            dropdown_text_color="white",
            button_color="#404040",
            button_hover_color="#505050",
            border_color="#404040",
            fg_color="#2b2b2b",
            text_color="white"
        )
        self.category_combo.pack(side=ctk.LEFT, fill=ctk.X, expand=True)
        self.category_combo.configure(command=lambda _: self.on_category_select_callback())
        
        # Инициализируем первую категорию, если она есть
        if categories:
            self.category_combo.set(categories[0])
        
        # Правая часть - кнопки действий
        right_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        right_frame.pack(side=ctk.RIGHT, padx=(15, 0))
        
        ctk.CTkButton(
            right_frame, 
            text="➕ Добавить", 
            command=self.on_add_category,
            width=130,
            height=36,
            corner_radius=6,
            font=("Segoe UI Emoji", 12)
        ).pack(side=ctk.LEFT, padx=3)
        
        ctk.CTkButton(
            right_frame, 
            text="✏️ Редактировать", 
            command=self.on_edit_category,
            width=150,
            height=36,
            corner_radius=6,
            font=("Segoe UI Emoji", 12)
        ).pack(side=ctk.LEFT, padx=3)
        
        ctk.CTkButton(
            right_frame, 
            text="➕ Новый шаблон", 
            command=self.on_add_template,
            width=150,
            height=36,
            corner_radius=6,
            font=("Segoe UI Emoji", 12)
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