"""
Генератор иконок из эмодзи для использования в CustomTkinter
Использует Twemoji для высококачественных цветных иконок
"""
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import customtkinter as ctk
import sys
import io
import requests
from urllib.parse import quote
import emoji as emoji_lib


class EmojiIconButton:
    """Генератор иконок-кнопок из эмодзи с использованием Twemoji"""
    
    _icon_cache = {}
    _ctk_image_cache = {}
    TWEMOJI_CDN = "https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72"
    
    @staticmethod
    def emoji_to_codepoint(emoji_str: str) -> str:
        """Конвертирует эмодзи в кодпоинт для Twemoji"""
        try:
            # Специальные замены для символов, которых нет в Twemoji
            replacements = {
                '☆': '2b50',  # Пустая звезда -> полная звезда (будем использовать fallback)
                '✏️': '270f-fe0f',  # Карандаш
                '✏': '270f',  # Карандаш без вариации
            }
            
            if emoji_str in replacements:
                return replacements[emoji_str]
            
            codepoints = []
            for char in emoji_str:
                if ord(char) > 0xFFFF:
                    # Это суррогатная пара
                    codepoints.append(f"{ord(char):x}")
                else:
                    codepoints.append(f"{ord(char):x}")
            return "-".join(codepoints)
        except:
            return None
    
    @staticmethod
    def download_twemoji(emoji_str: str, size: int = 72) -> Image.Image:
        """Скачивает красивый цветной эмодзи с CDN Twemoji"""
        try:
            import ssl
            import urllib.request
            
            codepoint = EmojiIconButton.emoji_to_codepoint(emoji_str)
            if not codepoint:
                return None
            
            url = f"{EmojiIconButton.TWEMOJI_CDN}/{codepoint}.png"
            
            # Отключаем проверку SSL для локальной сети
            ssl._create_default_https_context = ssl._create_unverified_context
            
            try:
                response = requests.get(url, timeout=5, verify=False)
                if response.status_code == 200:
                    img = Image.open(io.BytesIO(response.content))
                    return img
            except:
                # Пробуем через urllib если requests не работает
                with urllib.request.urlopen(url, context=ssl._create_unverified_context()) as response:
                    img = Image.open(io.BytesIO(response.read()))
                    return img
        except Exception as e:
            print(f"Не удалось скачать Twemoji для {emoji_str}: {e}")
        
        return None
    
    @staticmethod
    def create_emoji_image_twemoji(emoji: str, size: int = 32) -> Image.Image:
        """
        Создаёт PIL Image с КРАСИВЫМ цветным эмодзи от Twemoji
        
        Args:
            emoji: Эмодзи символ
            size: Размер изображения
            
        Returns:
            PIL Image объект
        """
        try:
            # Скачиваем высокое качество (72x72)
            twemoji_img = EmojiIconButton.download_twemoji(emoji, 72)
            
            if twemoji_img:
                # Делаем прозрачный фон
                if twemoji_img.mode != 'RGBA':
                    twemoji_img = twemoji_img.convert('RGBA')
                
                # Масштабируем до нужного размера
                twemoji_img = twemoji_img.resize((size, size), Image.Resampling.LANCZOS)
                return twemoji_img
            
            return None
        except Exception as e:
            print(f"Ошибка при создании Twemoji: {e}")
            return None
    
    @staticmethod
    def create_fallback_emoji(emoji: str, size: int = 32) -> Image.Image:
        """Fallback - создаёт эмодзи если Twemoji недоступен"""
        try:
            # Цветовая палитра
            EMOJI_COLORS = {
                '⚙️': (66, 133, 244),      # Settings - синий Google
                '📊': (251, 188, 4),       # Statistics - жёлтый Google
                '🗑️': (234, 67, 53),       # Trash - красный Google
                '📝': (52, 168, 83),       # Edit - зелёный Google
                '📋': (156, 39, 176),      # Copy - фиолетовый
                '⭐': (255, 193, 7),       # Star - золотой
                '☆': (189, 189, 189),      # Empty star - светло-серый
                '🔨': (191, 144, 0),       # Hammer - коричневый
                '🔒': (3, 155, 229),       # Lock - голубой
                '🔓': (158, 158, 158),     # Unlock - серый
                '👁️': (66, 133, 244),      # Eye - синий
                '✓': (52, 168, 83),        # Check - зелёный
                '✏️': (66, 133, 244),      # Pencil - синий
                '✏': (66, 133, 244),       # Pencil - синий
                '💾': (66, 133, 244),      # Save - синий
                '➕': (52, 168, 83),       # Plus - зелёный
            }
            
            temp_size = size * 4
            temp_img = Image.new('RGBA', (temp_size, temp_size), color=(0, 0, 0, 0))
            temp_draw = ImageDraw.Draw(temp_img)
            
            font_size = int(temp_size * 0.75)
            font = None
            
            try:
                font = ImageFont.truetype("C:\\Windows\\Fonts\\seguiemj.ttf", font_size)
            except:
                try:
                    font = ImageFont.truetype("C:\\Windows\\Fonts\\segoeui.ttf", font_size)
                except:
                    font = ImageFont.load_default()
            
            # Получаем размеры
            left, top, right, bottom = temp_draw.textbbox((0, 0), emoji, font=font)
            text_width = right - left
            text_height = bottom - top
            
            x = (temp_size - text_width) // 2 - left
            y = (temp_size - text_height) // 2 - top
            
            # Рисуем белым
            temp_draw.text((x, y), emoji, font=font, fill=(255, 255, 255, 255))
            
            # Масштабируем вниз
            final_img = temp_img.resize((size, size), Image.Resampling.LANCZOS)
            
            # Применяем цвет
            color = EMOJI_COLORS.get(emoji, (100, 150, 255))
            colored = Image.new('RGBA', final_img.size, color=(0, 0, 0, 0))
            
            for x_p in range(final_img.width):
                for y_p in range(final_img.height):
                    pixel = final_img.getpixel((x_p, y_p))
                    if len(pixel) >= 4:
                        _, _, _, alpha = pixel
                    else:
                        alpha = 255
                    
                    if alpha > 0:
                        colored.putpixel((x_p, y_p), (*color, alpha))
            
            return colored
        except Exception as e:
            print(f"Ошибка fallback: {e}")
            return None
    
    @staticmethod
    def create_emoji_image(emoji: str, size: int = 32, bg_color: str = "#2b2b2b") -> Image.Image:
        """
        Создаёт PIL Image с КРАСИВЫМ ЦВЕТНЫМ эмодзи (Twemoji)
        
        Args:
            emoji: Эмодзи символ
            size: Размер изображения
            bg_color: Цвет фона (не используется)
            
        Returns:
            PIL Image объект
        """
        # Проверяем кеш
        cache_key = f"{emoji}_{size}"
        if cache_key in EmojiIconButton._icon_cache:
            return EmojiIconButton._icon_cache[cache_key]
        
        # Сначала пробуем Twemoji
        img = EmojiIconButton.create_emoji_image_twemoji(emoji, size)
        
        # Если Twemoji не сработал, используем fallback
        if img is None:
            img = EmojiIconButton.create_fallback_emoji(emoji, size)
        
        # Сохраняем в кеш
        if img is not None:
            EmojiIconButton._icon_cache[cache_key] = img
        
        return img
    
    @staticmethod
    def get_ctk_image(emoji: str, size: int = 32, bg_color: str = "#2b2b2b"):
        """
        Получить CTkImage для использования в кнопках (С КЕШИРОВАНИЕМ!)
        
        Args:
            emoji: Эмодзи символ
            size: Размер иконки
            bg_color: Цвет фона
            
        Returns:
            CTkImage объект
        """
        # Проверяем кеш CTkImage
        cache_key = f"ctk_{emoji}_{size}"
        if cache_key in EmojiIconButton._ctk_image_cache:
            return EmojiIconButton._ctk_image_cache[cache_key]
        
        try:
            # Создаём светлую версию (light mode)
            light_img = EmojiIconButton.create_emoji_image(emoji, size, bg_color)
            # Создаём тёмную версию
            dark_img = EmojiIconButton.create_emoji_image(emoji, size, "#1a1a1a")
            
            if light_img and dark_img:
                # Создаём CTkImage
                ctk_img = ctk.CTkImage(light_image=light_img, dark_image=dark_img, size=(size, size))
                
                # Сохраняем в кеш
                EmojiIconButton._ctk_image_cache[cache_key] = ctk_img
                return ctk_img
        except Exception as e:
            print(f"Ошибка создания CTkImage: {e}")
        
        return None
    
    @staticmethod
    def preload_common_icons():
        """Предзагрузка часто используемых иконок для ускорения UI"""
        common_icons = [
            ('📋', 16),  # Copy
            ('📝', 16),  # Edit
            ('➕', 16),  # Add
            ('🗑️', 16),  # Delete
            ('💾', 16),  # Save
            ('⭐', 20),  # Star filled
            ('☆', 20),   # Star empty
            ('⚙️', 20),  # Settings
            ('📊', 20),  # Statistics
        ]
        
        for emoji, size in common_icons:
            # Загружаем иконки в фоне
            try:
                EmojiIconButton.get_ctk_image(emoji, size)
            except:
                pass


def create_emoji_button_text(emoji: str, text: str) -> str:
    """
    Создаёт текст кнопки с эмодзи
    
    Args:
        emoji: Эмодзи символ
        text: Текст для кнопки
        
    Returns:
        str: Комбинированный текст
    """
    return f"{emoji} {text}"

