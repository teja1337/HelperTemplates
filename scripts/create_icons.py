"""
Создание иконок для Helper
- app_icon.ico: для приложения
- installer_icon.ico: для установщика
"""
from PIL import Image, ImageDraw, ImageFont
import os

def create_app_icon():
    """Создать иконку приложения (более красивая версия)"""
    
    sizes = [16, 32, 48, 64, 128, 256]
    images = []
    
    for size in sizes:
        # Создаём изображение с прозрачностью
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Рисуем красивый градиент синий->голубой
        for i in range(size):
            # Радиальный градиент от центра
            dx = i - size/2
            
            for j in range(size):
                dy = j - size/2
                distance = (dx*dx + dy*dy) ** 0.5
                
                if distance < size/2:
                    # Сила градиента
                    intensity = 1 - (distance / (size/2))
                    
                    # Красивый синий цвет с градиентом
                    r = int(50 + intensity * 100)
                    g = int(150 + intensity * 80)
                    b = int(255)
                    
                    img.putpixel((i, j), (r, g, b, 255))
        
        # Добавляем букву "H" белым цветом с тенью
        try:
            font_size = int(size * 0.65)
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()
        
        text = "H"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (size - text_width) / 2
        y = (size - text_height) / 2 - bbox[1]
        
        # Тень (чёрная полупрозрачная)
        draw.text((x+2, y+2), text, font=font, fill=(0, 0, 0, 150))
        # Основной текст (белый)
        draw.text((x, y), text, font=font, fill=(255, 255, 255, 255))
        
        images.append(img)
    
    # Сохраняем как иконку приложения
    icon_path = os.path.join(os.path.dirname(__file__), 'icon.ico')
    images[0].save(icon_path, format='ICO', sizes=[(s, s) for s in sizes])
    
    print(f"✅ Иконка приложения создана: {icon_path}")
    print(f"   Размеры: {', '.join(str(s)+'x'+str(s) for s in sizes)}")
    
    # Также сохраняем отдельно для установщика
    icon_path_installer = os.path.join(os.path.dirname(__file__), 'installer_icon.ico')
    images[0].save(icon_path_installer, format='ICO', sizes=[(s, s) for s in sizes])
    print(f"✅ Иконка установщика создана: {icon_path_installer}")
    
    return icon_path

if __name__ == "__main__":
    create_app_icon()
