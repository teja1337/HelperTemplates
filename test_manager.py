#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Тестовый скрипт для проверки TemplateManager"""

import sys
sys.path.insert(0, '.')

from models.template_manager import TemplateManager

def test_manager():
    print("=== Тест TemplateManager ===\n")
    
    # Создаем менеджер
    manager = TemplateManager()
    
    # Проверяем типы категорий
    print(f"Доступные типы: {manager.get_category_types()}")
    print(f"Текущий тип: {manager.current_category_type}")
    print(f"Текущий файл: {manager.get_current_filename()}\n")
    
    # Проверяем категории для Клиентов
    print(f"Категории Клиентов: {manager.get_categories()}")
    
    # Переключаемся на Коллег
    print("\n--- Переключаемся на Коллег ---")
    manager.set_category_type("Коллеги")
    print(f"Текущий тип: {manager.current_category_type}")
    print(f"Текущий файл: {manager.get_current_filename()}")
    print(f"Категории Коллег: {manager.get_categories()}")
    
    # Переключаемся обратно
    print("\n--- Переключаемся обратно на Клиентов ---")
    manager.set_category_type("Клиенты")
    print(f"Текущий тип: {manager.current_category_type}")
    print(f"Категории Клиентов: {manager.get_categories()}")
    
    print("\n=== Тест завершён успешно! ===")

if __name__ == "__main__":
    test_manager()
