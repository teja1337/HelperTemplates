"""
Многопоточный поиск для UI без зависания
"""
from typing import Callable, List
from threading import Thread
from queue import Queue
import time


class ThreadedSearcher:
    """
    Поиск в отдельном потоке с передачей результатов через Queue.
    
    UI отправляет запрос -> поиск выполняется в фоне -> результаты
    поступают в очередь -> UI обновляется без задержек.
    """
    
    def __init__(self, on_results_callback: Callable[[List[dict]], None]):
        """
        Args:
            on_results_callback: Функция вызывается с результатами поиска
        """
        self.on_results_callback = on_results_callback
        self.results_queue: Queue = Queue()
        self.search_thread = None
        self.is_running = False
        self.current_query = None
        self.current_category = None
    
    def start_search(self, query: str, category: str, search_func: Callable) -> None:
        """
        Запустить поиск в отдельном потоке.
        
        Args:
            query: Поисковый запрос
            category: Категория для поиска
            search_func: Функция search(query, category) -> List[dict]
        """
        # Отменяем предыдущий поиск
        self.is_running = False
        if self.search_thread and self.search_thread.is_alive():
            self.search_thread.join(timeout=0.1)
        
        # Запускаем новый поиск
        self.current_query = query
        self.current_category = category
        self.is_running = True
        
        self.search_thread = Thread(
            target=self._search_worker,
            args=(query, category, search_func),
            daemon=True
        )
        self.search_thread.start()
    
    def _search_worker(self, query: str, category: str, search_func: Callable) -> None:
        """Рабочая функция потока"""
        try:
            # Выполняем поиск
            results = search_func(query, category)
            
            # Отправляем результаты в очередь (если поиск не был отменен)
            if self.is_running and self.current_query == query:
                self.results_queue.put(results)
        except Exception as e:
            print(f"[ERROR] Ошибка при поиске: {e}")
            if self.is_running:
                self.results_queue.put([])  # Пустой результат при ошибке
    
    def get_results(self) -> List[dict] | None:
        """
        Получить результаты поиска, если они готовы.
        Не блокирует UI (non-blocking).
        
        Returns:
            Список результатов или None если ещё не готовы
        """
        try:
            return self.results_queue.get_nowait()
        except:
            return None
    
    def stop_search(self) -> None:
        """Остановить текущий поиск"""
        self.is_running = False
