"""
Точка входа приложения Template Helper
"""
import customtkinter as ctk
from models.template_manager import TemplateManager
from views.main_window import MainWindow
from views.welcome_window import WelcomeWindow
from config import UI_CONFIG
from config.settings import PATHS


def main():
    """Основная функция приложения"""
    # Настройка темы customtkinter
    ctk.set_appearance_mode(UI_CONFIG.APPEARANCE_MODE)
    ctk.set_default_color_theme(UI_CONFIG.COLOR_THEME)
    
    # Создание корневого окна
    root = ctk.CTk()
    
    # Проверка первого запуска
    if PATHS.is_first_run():
        # Показать приветственное окно
        welcome = WelcomeWindow(root)
        root.wait_window(welcome)  # Ждать закрытия окна приветствия
        
        # Отметить, что первый запуск завершен
        PATHS.mark_first_run_complete()
    
    # Инициализация менеджера шаблонов
    template_manager = TemplateManager()
    
    # Создание главного окна приложения
    app = MainWindow(root, template_manager)
    
    # Запуск главного цикла
    root.mainloop()


if __name__ == "__main__":
    main()