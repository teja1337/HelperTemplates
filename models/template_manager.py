"""
Менеджер шаблонов для работы с категориями и текстовыми шаблонами
"""
import json
import os
from typing import List, Dict, Optional
from config.settings import CATEGORIES, PATHS


class TemplateManager:
    """
    Класс для управления шаблонами и категориями
    
    Attributes:
        current_category_type (str): Текущий выбранный тип категорий
        files (dict): Словарь путей к файлам для каждого типа категорий
        categories (dict): Словарь с категориями и их шаблонами
    """
    
    def __init__(self):
        """Инициализация менеджера шаблонов"""
        # Создаём директорию данных если её нет
        os.makedirs(PATHS.APP_DATA_DIR, exist_ok=True)
        
        # Текущий тип категорий
        self.current_category_type = CATEGORIES.CLIENTS
        
        # Пути к файлам для разных типов категорий
        self.files = {
            CATEGORIES.CLIENTS: PATHS.TEMPLATES_CLIENTS,
            CATEGORIES.COLLEAGUES: PATHS.TEMPLATES_COLLEAGUES
        }
        
        # Категории и шаблоны
        self.categories: Dict[str, List[Dict]] = {}
        
        # Загружаем шаблоны
        self.load_templates()
    
    def get_current_filename(self) -> str:
        """
        Получить имя файла для текущего типа категорий
        
        Returns:
            str: Полный путь к файлу
        """
        return self.files[self.current_category_type]
    
    def load_templates(self) -> None:
        """Загрузка шаблонов из файла текущего типа"""
        filename = self.get_current_filename()
        
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    self.categories = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Ошибка при загрузке шаблонов из {filename}: {e}")
                self._create_default_templates()
        else:
            self._create_default_templates()
    
    def _create_default_templates(self) -> None:
        """Создание демо-шаблонов при первом запуске"""
        if self.current_category_type == CATEGORIES.CLIENTS:
            self.categories = {
                "Приветствие": [
                    {"title": "Стандартное приветствие", "text": "Здравствуйте! Чем могу помочь?"}
                ],
                "Прощание": [
                    {"title": "Стандартное прощание", "text": "Всего доброго! Обращайтесь еще!"}
                ]
            }
        else:  # CATEGORIES.COLLEAGUES
            self.categories = {
                "Общение": [
                    {"title": "Привет", "text": "Привет! Как дела?"}
                ]
            }
        
        self.save_templates()
    
    def save_templates(self) -> bool:
        """
        Сохранение шаблонов в файл текущего типа
        
        Returns:
            bool: True если сохранение успешно, False в случае ошибки
        """
        try:
            filename = self.get_current_filename()
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.categories, f, ensure_ascii=False, indent=2)
            return True
        except IOError as e:
            print(f"Ошибка при сохранении шаблонов: {e}")
            return False
    
    def set_category_type(self, category_type: str) -> bool:
        """
        Установить текущий тип категорий и загрузить его шаблоны
        
        Args:
            category_type (str): Тип категорий (CATEGORIES.CLIENTS или CATEGORIES.COLLEAGUES)
        
        Returns:
            bool: True если тип установлен успешно
        """
        if category_type in self.files:
            self.current_category_type = category_type
            self.load_templates()
            return True
        return False
    
    def get_category_types(self) -> List[str]:
        """
        Получить список типов категорий
        
        Returns:
            List[str]: Список всех доступных типов категорий
        """
        return list(self.files.keys())
    
    def get_categories(self) -> List[str]:
        """
        Получить список категорий
        
        Returns:
            List[str]: Список названий категорий
        """
        return list(self.categories.keys())
    
    def add_category(self, category_name: str) -> bool:
        """
        Добавить новую категорию
        
        Args:
            category_name (str): Название новой категории
        
        Returns:
            bool: True если категория добавлена успешно
        """
        if not category_name or category_name in self.categories:
            return False
        
        self.categories[category_name] = []
        return self.save_templates()
    
    def rename_category(self, old_name: str, new_name: str) -> bool:
        """
        Переименовать категорию
        
        Args:
            old_name (str): Старое название категории
            new_name (str): Новое название категории
        
        Returns:
            bool: True если категория переименована успешно
        """
        if old_name not in self.categories or not new_name or new_name in self.categories:
            return False
        
        self.categories[new_name] = self.categories.pop(old_name)
        return self.save_templates()
    
    def delete_category(self, category_name: str) -> bool:
        """
        Удалить категорию
        
        Args:
            category_name (str): Название категории для удаления
        
        Returns:
            bool: True если категория удалена успешно
        """
        if category_name not in self.categories:
            return False
        
        del self.categories[category_name]
        return self.save_templates()
    
    def get_templates(self, category: str) -> List[Dict]:
        """
        Получить шаблоны для категории
        
        Args:
            category (str): Название категории
        
        Returns:
            List[Dict]: Список шаблонов в категории
        """
        return self.categories.get(category, [])
    
    def add_template(self, category: str, title: str, text: str) -> bool:
        """
        Добавить шаблон в категорию
        
        Args:
            category (str): Название категории
            title (str): Заголовок шаблона
            text (str): Текст шаблона
        
        Returns:
            bool: True если шаблон добавлен успешно
        """
        if category not in self.categories:
            return False
        
        self.categories[category].append({"title": title, "text": text})
        return self.save_templates()
    
    def edit_template(self, category: str, index: int, new_title: str, new_text: str) -> bool:
        """
        Редактировать шаблон
        
        Args:
            category (str): Название категории
            index (int): Индекс шаблона в категории
            new_title (str): Новый заголовок
            new_text (str): Новый текст
        
        Returns:
            bool: True если шаблон отредактирован успешно
        """
        if category not in self.categories:
            return False
        
        if not (0 <= index < len(self.categories[category])):
            return False
        
        self.categories[category][index] = {"title": new_title, "text": new_text}
        return self.save_templates()
    
    def delete_template(self, category: str, index: int) -> bool:
        """
        Удалить шаблон из категории
        
        Args:
            category (str): Название категории
            index (int): Индекс шаблона для удаления
        
        Returns:
            bool: True если шаблон удалён успешно
        """
        if category not in self.categories:
            return False
        
        if not (0 <= index < len(self.categories[category])):
            return False
        
        self.categories[category].pop(index)
        return self.save_templates()