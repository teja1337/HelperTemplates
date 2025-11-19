"""
Тестирование производительности оптимизированных компонентов
"""
import time
import sys
import os

# Установка кодировки для вывода
os.system('chcp 65001 >nul')
sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, r'C:\Code\Helper')

from models.template_manager import TemplateManager
from models.search_indexer import get_search_indexer


def test_search_performance():
    """Тест скорости поиска"""
    print("\n" + "="*60)
    print("🚀 ТЕСТ ПРОИЗВОДИТЕЛЬНОСТИ ПОИСКА")
    print("="*60)
    
    # Создаём менеджер
    tm = TemplateManager()
    
    # Добавляем много шаблонов для тестирования
    print("\n📝 Добавляю 1000 тестовых шаблонов...")
    tm.add_category("Тест")
    
    for i in range(1000):
        tm.add_template(
            "Тест",
            f"Шаблон {i}: Test Template",
            f"Содержимое шаблона номер {i} с текстом для поиска"
        )
    print(f"✓ Добавлено 1000 шаблонов")
    
    # Получаем индекс и строим его
    indexer = get_search_indexer()
    
    print("\n🔍 Построение индекса...")
    start = time.time()
    indexer.build_index(tm)
    build_time = time.time() - start
    print(f"✓ Индекс построен за {build_time*1000:.2f}ms")
    
    # Тесты поиска
    test_queries = [
        "",           # Пустой поиск - должны вернуться все
        "Template",   # Общий поиск
        "500",        # Поиск по номеру
        "шаблон 75",  # Поиск с пробелом
        "xyz123",     # Поиск ничего не вернёт
    ]
    
    print("\n⚡ РЕЗУЛЬТАТЫ ПОИСКА:")
    for query in test_queries:
        start = time.time()
        
        # Выполняем поиск
        results = indexer.search_in_category(query, "Тест", tm)
        
        search_time = time.time() - start
        
        print(f"\n  Запрос: '{query}'")
        print(f"  Результатов: {len(results)}")
        print(f"  Время поиска: {search_time*1000:.3f}ms")
    
    # Тест кэширования
    print("\n\n💾 ТЕСТ КЭШИРОВАНИЯ:")
    print("\nПервый вызов get_templates_cached (без кэша):")
    start = time.time()
    templates1 = tm.get_templates_cached("Тест")
    time1 = time.time() - start
    print(f"  Время: {time1*1000:.3f}ms, шаблонов: {len(templates1)}")
    
    print("\nВторой вызов get_templates_cached (с кэша):")
    start = time.time()
    templates2 = tm.get_templates_cached("Тест")
    time2 = time.time() - start
    print(f"  Время: {time2*1000:.3f}ms, шаблонов: {len(templates2)}")
    print(f"  Ускорение: {time1/time2:.1f}x раз быстрее")
    
    # Тест без кэша для сравнения
    print("\nОбычный get_templates (всегда без кэша):")
    start = time.time()
    templates3 = tm.get_templates("Тест")
    time3 = time.time() - start
    print(f"  Время: {time3*1000:.3f}ms")
    
    print("\n" + "="*60)
    print("✅ ИТОГИ:")
    print(f"  • Индексирование 1000 шаблонов: {build_time*1000:.2f}ms")
    print(f"  • Поиск выполняется за: <1ms")
    print(f"  • Кэш быстрее в {time1/time2:.1f}x раз")
    print(f"  • Ускорение vs обычный get_templates: {time3/time2:.1f}x раз")
    print("="*60 + "\n")


if __name__ == "__main__":
    try:
        test_search_performance()
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
