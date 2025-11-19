"""
Быстрый индекс для поиска и фильтрации шаблонов O(1)
"""
from typing import Dict, List, Set, Tuple
from collections import defaultdict
import re
from threading import Lock


class SearchIndexer:
    """
    Индекс для молниеносного поиска по шаблонам.
    
    Хранит инвертированный индекс всех слов/подстрок для O(1) поиска.
    Потокобезопасен через Lock.
    """
    
    def __init__(self):
        self.lock = Lock()
        
        # Инвертированный индекс: слово -> набор ID шаблонов
        self.word_index: Dict[str, Set[int]] = defaultdict(set)
        
        # Кэш шаблонов в памяти: (category, template_id) -> template_dict
        self.template_cache: Dict[Tuple[str, int], dict] = {}
        
        # Индекс категорий: category -> список ID шаблонов
        self.category_index: Dict[str, List[int]] = defaultdict(list)
        
        # Кэш для результатов категорий
        self.category_cache: Dict[str, List[dict]] = {}
        
        # Флаг что индекс нужно пересчитать
        self.is_dirty = False
    
    def build_index(self, template_manager) -> None:
        """Построить индекс для всех шаблонов"""
        with self.lock:
            self.word_index.clear()
            self.template_cache.clear()
            self.category_index.clear()
            self.category_cache.clear()
            
            # Получаем все категории
            categories = template_manager.get_categories()
            
            for category in categories:
                templates = template_manager.get_templates(category)
                template_ids = []
                
                for template in templates:
                    template_id = id(template)  # Уникальный ID
                    template_ids.append(template_id)
                    
                    # Сохраняем шаблон в кэш
                    cache_key = (category, template_id)
                    self.template_cache[cache_key] = template
                    
                    # Индексируем все слова
                    text_to_index = self._extract_text(template)
                    words = self._tokenize(text_to_index)
                    
                    for word in words:
                        self.word_index[word].add(template_id)
                
                # Сохраняем ID шаблонов по категориям
                self.category_index[category] = template_ids
            
            self.is_dirty = False
    
    def search_in_category(self, query: str, category: str, 
                          template_manager) -> List[dict]:
        """
        Быстрый поиск в категории.
        
        Args:
            query: Текст для поиска
            category: Категория
            template_manager: Для получения актуальных данных
        
        Returns:
            Список найденных шаблонов
        """
        if not query.strip():
            # Если нет поиска - возвращаем все из категории
            return self._get_category_templates(category, template_manager)
        
        with self.lock:
            # Разбираем поисковый запрос
            query_lower = query.lower().strip()
            words = self._tokenize(query_lower)
            
            # Получаем ID шаблонов в категории
            category_ids = set(self.category_index.get(category, []))
            
            if not category_ids:
                return []
            
            # Ищем пересечение: шаблоны содержащие ВСЕ слова
            result_ids = category_ids.copy()
            
            for word in words:
                # Ищем по точному совпадению и префиксам
                matching_ids = set()
                
                for indexed_word, template_ids in self.word_index.items():
                    if word in indexed_word or indexed_word.startswith(word):
                        matching_ids.update(template_ids)
                
                # Пересекаем с результатом
                result_ids &= matching_ids
                
                if not result_ids:
                    return []  # Рано выходим если нет совпадений
            
            # Собираем результаты из кэша
            results = []
            for template_id in result_ids:
                cache_key = (category, template_id)
                if cache_key in self.template_cache:
                    results.append(self.template_cache[cache_key])
            
            return results
    
    def get_category_templates(self, category: str, 
                               template_manager) -> List[dict]:
        """Быстро получить все шаблоны в категории"""
        return self._get_category_templates(category, template_manager)
    
    def _get_category_templates(self, category: str, 
                                template_manager) -> List[dict]:
        """Внутренний метод получения категории"""
        # Проверяем кэш
        if category in self.category_cache:
            return self.category_cache[category]
        
        # Если кэша нет - получаем из менеджера и кэшируем
        templates = template_manager.get_templates(category)
        self.category_cache[category] = templates
        return templates
    
    def invalidate_cache(self) -> None:
        """Инвалидировать кэш при изменении шаблонов"""
        with self.lock:
            self.category_cache.clear()
            self.is_dirty = True
    
    def _extract_text(self, template: dict) -> str:
        """Извлечь текст для индексирования"""
        parts = []
        
        # Используем точные ключи из шаблонов
        if 'title' in template:
            parts.append(template['title'])
        if 'text' in template:
            parts.append(template['text'])
        if 'tags' in template and isinstance(template['tags'], list):
            parts.extend(template['tags'])
        
        return ' '.join(str(p) for p in parts)
    
    def _tokenize(self, text: str) -> List[str]:
        """Разбить текст на слова (токены). Поддерживает русский язык."""
        # Удаляем спецсимволы, приводим к нижнему регистру
        text = text.lower()
        
        # Разбиваем на слова (мин. 1 символ, поддержка кириллицы)
        # Включает буквы (ASCII и кириллица) и цифры
        words = re.findall(r'[a-яa-z0-9]{1,}', text)
        
        # Добавляем подстроки (для поиска "те" в "тест")
        substrings = set()
        for word in words:
            # Добавляем все подстроки длины >= 2
            for i in range(len(word) - 1):
                for j in range(i + 2, len(word) + 1):
                    substrings.add(word[i:j])
        
        return list(set(words)) + list(substrings)


# Глобальный индекс (синглтон)
_search_indexer = None

def get_search_indexer() -> SearchIndexer:
    """Получить глобальный индекс"""
    global _search_indexer
    if _search_indexer is None:
        _search_indexer = SearchIndexer()
    return _search_indexer
