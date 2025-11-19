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
        
        # Оптимизация: отложенное сохранение
        self._save_pending = False
        self._save_timer_id = None
        
        # Кэш категорий (для быстрого доступа)
        self._category_cache: Dict[str, List[Dict]] = {}
        self._cache_dirty = True
        
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
                    data = json.load(f)
                    # Валидация структуры
                    if isinstance(data, dict):
                        self.categories = self._validate_templates(data)
                    else:
                        raise ValueError("Неверный формат JSON")
            except (json.JSONDecodeError, IOError, ValueError) as e:
                print(f"Ошибка при загрузке шаблонов из {filename}: {e}")
                self._create_default_templates()
        else:
            self._create_default_templates()
    
    def _validate_templates(self, data: dict) -> dict:
        """Валидация загруженных шаблонов"""
        MAX_TEXT_LENGTH = 50000  # Максимум 50KB текста на шаблон
        validated = {}
        
        for category, templates in data.items():
            if not isinstance(templates, list):
                continue
            
            valid_templates = []
            for template in templates:
                if not isinstance(template, dict):
                    continue
                
                title = template.get('title', '').strip()
                text = template.get('text', '').strip()
                
                # Пропускаем пустые или очень большие шаблоны
                if not title or not text or len(text) > MAX_TEXT_LENGTH:
                    continue
                
                # Включаем валидный шаблон
                valid_templates.append({
                    'title': title[:200],  # Ограничиваем заголовок
                    'text': text,
                    'pinned': template.get('pinned', False),
                    'stats': template.get('stats', {})
                })
            
            if valid_templates:
                validated[category] = valid_templates
        
        return validated if validated else self._get_default_templates()
    
    def _get_default_templates(self) -> dict:
        """Получить стандартные шаблоны по умолчанию"""
        if self.current_category_type == CATEGORIES.CLIENTS:
            return {
                "Приветствие": [
                    {"title": "Стандартное приветствие", "text": "Здравствуйте! Чем могу помочь?"}
                ],
                "Прощание": [
                    {"title": "Стандартное прощание", "text": "Всего доброго! Обращайтесь еще!"}
                ]
            }
        else:  # CATEGORIES.COLLEAGUES
            return {
                "Общение": [
                    {"title": "Привет", "text": "Привет! Как дела?"}
                ]
            }
    
    def _create_default_templates(self) -> None:
        """Создание демо-шаблонов при первом запуске"""
        self.categories = self._get_default_templates()
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
    
    def schedule_save(self, delay_ms: int = 500):
        """
        Отложенное сохранение для батчинга операций
        
        Args:
            delay_ms: Задержка в миллисекундах перед сохранением
        """
        import threading
        
        if self._save_timer_id:
            try:
                self._save_timer_id.cancel()
            except:
                pass
        
        def delayed_save():
            self.save_templates()
            self._save_pending = False
            self._save_timer_id = None
        
        self._save_pending = True
        self._save_timer_id = threading.Timer(delay_ms / 1000, delayed_save)
        self._save_timer_id.start()
    
    def force_save(self) -> bool:
        """
        Принудительное немедленное сохранение (отменяет отложенное)
        
        Returns:
            bool: True если сохранение успешно
        """
        if self._save_timer_id:
            self._save_timer_id.cancel()
            self._save_timer_id = None
        
        self._save_pending = False
        return self.save_templates()
    
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
        Получить шаблоны для категории, отсортированные по закреплению
        
        Args:
            category (str): Название категории
        
        Returns:
            List[Dict]: Список шаблонов в категории (закреплённые первыми)
        """
        templates = self.categories.get(category, [])
        # Сортируем: закреплённые (pinned=True) идут первыми
        return sorted(templates, key=lambda t: not t.get('pinned', False))
    
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
        self._invalidate_category_cache(category)
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
        self._invalidate_category_cache(category)
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
        self._invalidate_category_cache(category)
        return self.save_templates()
    
    def toggle_pin_template(self, category: str, index: int) -> bool:
        """
        Переключить закрепление шаблона (pinned/unpinned)
        
        Args:
            category (str): Название категории
            index (int): Индекс шаблона для переключения
        
        Returns:
            bool: True если операция успешна
        """
        if category not in self.categories:
            return False
        
        templates = self.categories[category]
        if not (0 <= index < len(templates)):
            return False
        
        # Переключаем состояние закрепления
        current_pinned = templates[index].get('pinned', False)
        templates[index]['pinned'] = not current_pinned
        self._invalidate_category_cache(category)
        
        return self.save_templates()
    
    def toggle_pin_template_by_name(self, category: str, template: dict) -> bool:
        """
        Переключить закрепление шаблона по названию
        
        Args:
            category (str): Название категории
            template (dict): Словарь с 'title' шаблона
        
        Returns:
            bool: True если операция успешна
        """
        if category not in self.categories:
            return False
        
        templates = self.categories[category]
        title = template.get('title')
        
        # Ищем только по названию (text может меняться при редактировании)
        for tpl in templates:
            if tpl.get('title') == title:
                # Переключаем состояние
                tpl['pinned'] = not tpl.get('pinned', False)
                self._invalidate_category_cache(category)
                return self.save_templates()
        
        return False
    
    def increment_usage(self, category: str, template: dict) -> bool:
        """
        Увеличить счётчик использований шаблона
        
        Args:
            category (str): Название категории
            template (dict): Словарь шаблона
        
        Returns:
            bool: True если операция успешна
        """
        if category not in self.categories:
            return False
        
        templates = self.categories[category]
        title = template.get('title')
        text = template.get('text')
        
        # Находим шаблон и увеличиваем счётчик
        for tpl in templates:
            if tpl.get('title') == title and tpl.get('text') == text:
                # Инициализируем stats если их нет
                if 'stats' not in tpl:
                    tpl['stats'] = {'usage_count': 0}
                
                tpl['stats']['usage_count'] = tpl['stats'].get('usage_count', 0) + 1
                # Используем отложенное сохранение для лучшей производительности
                self.schedule_save(delay_ms=1000)
                return True
        
        return False
    
    def get_top_used_templates(self, category: str, limit: int = 3) -> List[Dict]:
        """
        Получить топ используемых шаблонов в категории
        
        Args:
            category (str): Название категории
            limit (int): Количество шаблонов в топе
        
        Returns:
            List[Dict]: Список топ шаблонов, отсортированные по использованиям
        """
        if category not in self.categories:
            return []
        
        templates = self.categories[category]
        # Сортируем по usage_count в убывающем порядке
        sorted_templates = sorted(
            templates,
            key=lambda t: t.get('stats', {}).get('usage_count', 0),
            reverse=True
        )
        
        return sorted_templates[:limit]
    
    def get_template_stats(self, category: str, template: dict) -> dict:
        """
        Получить статистику шаблона
        
        Args:
            category (str): Название категории
            template (dict): Словарь шаблона
        
        Returns:
            dict: Статистика шаблона
        """
        if category not in self.categories:
            return {}
        
        templates = self.categories[category]
        
        for tpl in templates:
            if tpl.get('title') == template.get('title') and tpl.get('text') == template.get('text'):
                return tpl.get('stats', {'usage_count': 0})
        
        return {}
    
    def reset_statistics(self, category: str) -> bool:
        """
        Сбросить статистику всех шаблонов в категории
        
        Args:
            category (str): Название категории
        
        Returns:
            bool: True если сброс успешен, False в случае ошибка
        """
        if category not in self.categories:
            return False
        
        # Сбрасываем счётчик для всех шаблонов в категории
        for template in self.categories[category]:
            if 'stats' not in template:
                template['stats'] = {}
            template['stats']['usage_count'] = 0
        
        # Инвалидировать кэш
        self._invalidate_category_cache(category)
        
        # Сохраняем изменения
        return self.save_templates()
    
    def get_templates_cached(self, category: str) -> List[Dict]:
        """
        Получить шаблоны из кэша (если кэш свежий).
        Намного быстрее чем get_templates() для частых вызовов.
        
        Args:
            category: Название категории
        
        Returns:
            Список шаблонов
        """
        if not self._cache_dirty and category in self._category_cache:
            return self._category_cache[category]
        
        # Возвращаем и кэшируем
        templates = self.get_templates(category)
        self._category_cache[category] = templates
        self._cache_dirty = False
        return templates
    
    def _invalidate_category_cache(self, category: str = None) -> None:
        """Инвалидировать кэш"""
        if category:
            self._category_cache.pop(category, None)
        else:
            self._category_cache.clear()
        self._cache_dirty = True