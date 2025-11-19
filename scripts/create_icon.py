"""
Создание иконки для приложения Helper
"""
from PIL import Image, ImageDraw, ImageFont
import os

def create_icon():
    """Создать иконку с буквой H"""
    
    # Размеры для .ico файла (Windows поддерживает множественные размеры)
    sizes = [16, 32, 48, 64, 128, 256]
    images = []
    
    for size in sizes:
        # Создаём изображение с градиентом
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Рисуем круглый фон с градиентом (синий)
        for i in range(size):
            for j in range(size):
                # Расстояние от центра
                dx = i - size/2
                dy = j - size/2
                distance = (dx*dx + dy*dy) ** 0.5
                
                if distance < size/2:
                    # Градиент от светло-синего к тёмно-синему
                    intensity = 1 - (distance / (size/2))
                    r = int(30 + intensity * 50)
                    g = int(100 + intensity * 100)
                    b = int(200 + intensity * 55)
                    img.putpixel((i, j), (r, g, b, 255))
        
        # Добавляем букву "H"
        try:
            # Пытаемся использовать системный шрифт
            font_size = int(size * 0.6)
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            # Если не получается, используем стандартный
            font = ImageFont.load_default()
        
        # Рисуем "H" белым цветом
        text = "H"
        
        # Получаем размер текста для центрирования
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (size - text_width) / 2
        y = (size - text_height) / 2 - bbox[1]
        
        # Тень для текста
        draw.text((x+2, y+2), text, font=font, fill=(0, 0, 0, 100))
        # Основной текст
        draw.text((x, y), text, font=font, fill=(255, 255, 255, 255))
        
        images.append(img)
    
    # Сохраняем как .ico файл
    icon_path = os.path.join(os.path.dirname(__file__), 'icon.ico')
    images[0].save(icon_path, format='ICO', sizes=[(s, s) for s in sizes])
    
    print(f"✅ Иконка создана: {icon_path}")
    return icon_path

if __name__ == "__main__":
    create_icon()
