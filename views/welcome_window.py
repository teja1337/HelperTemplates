"""
Приветственное окно для первого запуска приложения
"""
import customtkinter as ctk
from config.settings import APP_NAME, APP_AUTHOR
from config.version import VERSION


class WelcomeWindow(ctk.CTkToplevel):
    """Окно приветствия при первом запуске"""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        # Настройки окна
        self.title("Добро пожаловать!")
        self.geometry("600x600")
        self.resizable(False, False)
        
        # Центрирование окна
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.winfo_screenheight() // 2) - (600 // 2)
        self.geometry(f"600x600+{x}+{y}")
        
        # Модальное окно
        self.transient(parent)
        self.grab_set()
        
        # Построить интерфейс
        self._build_ui()
        
        # Фокус на кнопку
        self.after(100, lambda: self.start_button.focus_set())
    
    def _build_ui(self):
        """Построить интерфейс окна"""
        # Основной контейнер с отступами
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=30, pady=30)
        
        # ==================== ЗАГОЛОВОК ====================
        title_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        title_frame.pack(fill="x", pady=(0, 20))
        
        # Эмодзи приветствия
        emoji_label = ctk.CTkLabel(
            title_frame,
            text="👋",
            font=("Segoe UI Emoji", 50)
        )
        emoji_label.pack(pady=(0, 8))
        
        # Название приложения
        app_name_label = ctk.CTkLabel(
            title_frame,
            text=APP_NAME,
            font=("Segoe UI", 28, "bold")
        )
        app_name_label.pack()
        
        # Версия
        version_label = ctk.CTkLabel(
            title_frame,
            text=f"версия {VERSION}",
            font=("Segoe UI", 13),
            text_color="gray"
        )
        version_label.pack(pady=(3, 0))
        
        # ==================== ОПИСАНИЕ ====================
        description_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        description_frame.pack(fill="x", pady=15)
        
        # Приветственный текст
        welcome_text = ctk.CTkLabel(
            description_frame,
            text="Добро пожаловать в Template Helper!",
            font=("Segoe UI", 16, "bold"),
            wraplength=500
        )
        welcome_text.pack(pady=(0, 12))
        
        # Описание возможностей
        features_text = (
            "Это приложение поможет вам:\n\n"
            "📝 Создавать и управлять текстовыми шаблонами\n"
            "📋 Быстро копировать нужный текст в буфер обмена\n"
            "🔍 Мгновенно находить шаблоны через поиск\n"
            "📌 Закреплять важные шаблоны для быстрого доступа\n"
            "📁 Организовывать шаблоны по категориям"
        )
        
        features_label = ctk.CTkLabel(
            description_frame,
            text=features_text,
            font=("Segoe UI", 13),
            justify="left",
            wraplength=500
        )
        features_label.pack(pady=8)
        
        # ==================== КНОПКА НАЧАТЬ ====================
        self.start_button = ctk.CTkButton(
            main_frame,
            text="✓ Понятно, начать работу",
            font=("Segoe UI", 16, "bold"),
            height=50,
            corner_radius=10,
            fg_color=("#2CC985", "#2FA572"),
            hover_color=("#27B574", "#28925F"),
            command=self._on_start
        )
        self.start_button.pack(fill="x", pady=(0, 10))
        
        # ==================== АВТОР ====================
        author_label = ctk.CTkLabel(
            main_frame,
            text=APP_AUTHOR,
            font=("Segoe UI", 11),
            text_color="gray"
        )
        author_label.pack()
        
        # Привязка Enter к кнопке
        self.bind("<Return>", lambda e: self._on_start())
        self.bind("<Escape>", lambda e: self._on_start())
    
    def _on_start(self):
        """Закрыть окно приветствия"""
        self.grab_release()
        self.destroy()
