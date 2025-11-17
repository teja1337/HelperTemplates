import tkinter as tk
from tkinter import ttk

class ModernTheme:
    """Современная тема для приложения"""
    
    def __init__(self):
        self.colors = {
            'primary': '#2E86AB',
            'primary_light': '#5FA8D3',
            'primary_dark': '#1B435D',
            'secondary': '#A23B72',
            'accent': '#F18F01',
            'background': '#F5F7FA',
            'surface': '#FFFFFF',
            'text_primary': '#2D3748',
            'text_secondary': '#718096',
            'border': '#E2E8F0',
            'success': '#48BB78',
            'warning': '#ED8936',
            'error': '#F56565',
            'status_success': '#48BB78',
            'status_info': '#2E86AB'
        }
        
        self.fonts = {
            'h1': ('Segoe UI', 16, 'bold'),
            'h2': ('Segoe UI', 14, 'bold'),
            'body': ('Segoe UI', 11),
            'button': ('Segoe UI', 10, 'bold'),
            'caption': ('Segoe UI', 9),
            'status': ('Segoe UI', 9)
        }
        
        self.setup_styles()
    
    def setup_styles(self):
        """Настройка стилей виджетов"""
        style = ttk.Style()
        
        # Современная тема
        style.theme_use('clam')
        
        # Настройка фреймов
        style.configure('Modern.TFrame', background=self.colors['background'])
        style.configure('Card.TFrame', 
                       background=self.colors['surface'],
                       relief='raised',
                       borderwidth=1)
        
        # Настройка меток
        style.configure('Modern.TLabel',
                       background=self.colors['background'],
                       foreground=self.colors['text_primary'],
                       font=self.fonts['body'])
        
        style.configure('Title.TLabel',
                       background=self.colors['background'],
                       foreground=self.colors['primary_dark'],
                       font=self.fonts['h1'])
        
        style.configure('CardTitle.TLabel',
                       background=self.colors['surface'],
                       foreground=self.colors['text_primary'],
                       font=self.fonts['h2'])
        
        # Стиль для статус-бара
        style.configure('Status.TLabel',
                       background=self.colors['surface'],
                       foreground=self.colors['text_secondary'],
                       font=self.fonts['status'],
                       borderwidth=1,
                       relief='sunken')
        
        style.configure('StatusSuccess.TLabel',
                       background=self.colors['status_success'],
                       foreground='white',
                       font=self.fonts['status'],
                       borderwidth=0)
        
        # Настройка кнопок
        style.configure('Primary.TButton',
                       background=self.colors['primary'],
                       foreground='white',
                       focuscolor=style.configure('.')['background'],
                       font=self.fonts['button'],
                       borderwidth=0,
                       relief='flat')
        
        style.map('Primary.TButton',
                 background=[('active', self.colors['primary_light']),
                           ('pressed', self.colors['primary_dark'])])
        
        style.configure('Secondary.TButton',
                       background=self.colors['surface'],
                       foreground=self.colors['primary'],
                       font=self.fonts['button'],
                       borderwidth=1,
                       relief='solid')
        
        style.map('Secondary.TButton',
                 background=[('active', self.colors['background'])])
        
        # Настройка комбобокса
        style.configure('Modern.TCombobox',
                       fieldbackground=self.colors['surface'],
                       background=self.colors['surface'],
                       foreground=self.colors['text_primary'],
                       borderwidth=1,
                       relief='solid')
        
        style.map('Modern.TCombobox',
                 fieldbackground=[('readonly', self.colors['surface'])],
                 selectbackground=[('readonly', self.colors['primary_light'])])
        
        # Настройка скроллбара
        style.configure('Modern.Vertical.TScrollbar',
                       background=self.colors['border'],
                       darkcolor=self.colors['border'],
                       lightcolor=self.colors['border'],
                       troughcolor=self.colors['background'],
                       bordercolor=self.colors['border'],
                       arrowcolor=self.colors['text_secondary'])
        
        style.map('Modern.Vertical.TScrollbar',
                 background=[('active', self.colors['primary'])])