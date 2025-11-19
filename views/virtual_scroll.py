"""
Виртуальная прокрутка - рендеринг только видимых шаблонов
"""
from typing import List, Callable, Dict
import customtkinter as ctk


class VirtualScrollFrame(ctk.CTkScrollableFrame):
    """
    Оптимизированный скролируемый фрейм.
    Рендерит только видимые элементы вместо всех сразу.
    
    Для 1000 шаблонов: вместо 1000 виджетов -> 10-20 видимых.
    """
    
    def __init__(self, parent, item_height: int = 100, **kwargs):
        """
        Args:
            parent: Родительский виджет
            item_height: Высота одного элемента в пикселях
        """
        super().__init__(parent, **kwargs)
        
        self.item_height = item_height
        self.items: List[dict] = []
        self.visible_widgets: Dict[int, ctk.CTkFrame] = {}
        self.item_creators: Dict[int, ctk.CTkFrame] = {}
        
        self.visible_start = 0
        self.visible_end = 0
        self.last_scroll_position = 0
        
        # Привязываем событие прокрутки
        self._scrollbar.bind("<MouseWheel>", self._on_scroll, add=True)
        self._scrollbar.bind("<Button-4>", self._on_scroll, add=True)
        self._scrollbar.bind("<Button-5>", self._on_scroll, add=True)
        self.bind("<MouseWheel>", self._on_scroll, add=True)
    
    def load_items(self, items: List[dict], create_widget_func: Callable) -> None:
        """
        Загрузить элементы для виртуальной прокрутки.
        
        Args:
            items: Список элементов (шаблонов)
            create_widget_func: Функция create_widget(parent, item) -> CTkFrame
        """
        # Очищаем старые виджеты
        for widget in self.visible_widgets.values():
            widget.destroy()
        self.visible_widgets.clear()
        self.item_creators.clear()
        
        self.items = items
        self.visible_start = 0
        self.visible_end = 0
        
        # Сохраняем функцию создания виджетов
        self.create_widget_func = create_widget_func
        
        # Устанавливаем высоту скролируемого контейнера
        total_height = len(items) * self.item_height
        self.configure(height=total_height)
        
        # Начальная отрисовка видимых элементов
        self._update_visible_items()
    
    def _on_scroll(self, event=None) -> None:
        """Событие прокрутки - обновляем видимые элементы"""
        self.after(10, self._update_visible_items)
    
    def _update_visible_items(self) -> None:
        """Обновить видимые элементы при прокрутке"""
        # Вычисляем какие элементы видны
        scroll_y = self._parent_canvas.yview()[0]
        visible_height = self._parent_canvas.winfo_height()
        
        new_start = int(scroll_y * len(self.items))
        new_end = min(new_start + visible_height // self.item_height + 2, len(self.items))
        
        # Если видимая область не изменилась - ничего не делаем
        if new_start == self.visible_start and new_end == self.visible_end:
            return
        
        # Удаляем элементы которые вышли из видимости
        for idx in list(self.visible_widgets.keys()):
            if idx < new_start or idx >= new_end:
                self.visible_widgets[idx].destroy()
                del self.visible_widgets[idx]
        
        # Добавляем новые элементы в видимую область
        for idx in range(new_start, new_end):
            if idx >= len(self.items):
                break
            
            if idx not in self.visible_widgets:
                # Создаём новый виджет
                try:
                    widget = self.create_widget_func(self, self.items[idx])
                    widget.pack(fill=ctk.X, padx=0, pady=0)
                    self.visible_widgets[idx] = widget
                except Exception as e:
                    print(f"[ERROR] Ошибка при создании виджета {idx}: {e}")
        
        self.visible_start = new_start
        self.visible_end = new_end
    
    def refresh_items(self, items: List[dict]) -> None:
        """Обновить список элементов"""
        self.load_items(items, self.create_widget_func)


class CompactVirtualList(ctk.CTkFrame):
    """
    Более лёгкий вариант виртуального списка.
    Для простых списков без сложной разметки.
    """
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.items = []
        self.visible_indices = set()
        
        # Холст для рисования
        self.canvas = ctk.CTkCanvas(
            self,
            bg="#1a1a1a",
            highlightthickness=0,
            height=300
        )
        self.canvas.pack(fill=ctk.BOTH, expand=True)
        
        # Скроллбар
        self.scrollbar = ctk.CTkScrollbar(
            self,
            command=self.canvas.yview,
            width=12
        )
        self.scrollbar.pack(side=ctk.RIGHT, fill=ctk.Y)
        self.canvas.config(yscrollcommand=self.scrollbar.set)
        
        # Привязываем прокрутку
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind("<Button-4>", self._on_mousewheel)
        self.canvas.bind("<Button-5>", self._on_mousewheel)
    
    def _on_mousewheel(self, event) -> None:
        """Обработка колёсика мыши"""
        if event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(3, "units")
        elif event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-3, "units")
