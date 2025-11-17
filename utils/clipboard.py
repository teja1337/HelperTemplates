import tkinter as tk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import tkinter as tk

def copy_to_clipboard(root: 'tk.Tk', text: str) -> bool:
    """
    Копирование текста в буфер обмена
    
    Args:
        root: Главное окно приложения
        text: Текст для копирования
    
    Returns:
        bool: Успешность операции
    """
    try:
        root.clipboard_clear()
        root.clipboard_append(text)
        root.update()  # Сохраняем в буфере после закрытия приложения
        return True
    except Exception:
        return False