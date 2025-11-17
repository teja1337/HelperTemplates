"""
Точка входа приложения Template Helper
"""
import customtkinter as ctk
from models.template_manager import TemplateManager
from views.main_window import MainWindow
from config import UI_CONFIG


def main():
    """Основная функция приложения"""
    # Настройка темы customtkinter
    ctk.set_appearance_mode(UI_CONFIG.APPEARANCE_MODE)
    ctk.set_default_color_theme(UI_CONFIG.COLOR_THEME)
    
    # Создание корневого окна
    root = ctk.CTk()
    
    # Инициализация менеджера шаблонов
    template_manager = TemplateManager()
    
    # Создание главного окна приложения
    app = MainWindow(root, template_manager)
    
    # Запуск главного цикла
    root.mainloop()


if __name__ == "__main__":
    main()