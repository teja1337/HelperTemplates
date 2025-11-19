"""
Updater - отдельное приложение для обновления Helper.exe
"""
import os
import shutil
import time
import sys
from pathlib import Path

def update_application():
    """Обновить основное приложение"""
    
    print("=" * 60)
    print("Запуск процесса обновления Helper...")
    print("=" * 60)
    
    # Определяем пути
    if getattr(sys, 'frozen', False):
        app_dir = Path(sys.executable).parent
    else:
        app_dir = Path(__file__).parent
    
    update_file = app_dir / "Helper_Installer.exe"
    main_file = app_dir / "Helper.exe"
    backup_file = app_dir / "Helper.exe.backup"
    
    try:
        # Ждем пока основное приложение закроется
        print("\nОжидание закрытия приложения...")
        time.sleep(3)
        
        # Проверяем наличие файла обновления
        if not update_file.exists():
            print(f"❌ Ошибка: файл обновления не найден: {update_file}")
            time.sleep(3)
            return
        
        # Создаем резервную копию
        if main_file.exists():
            print(f"\n📦 Создание резервной копии...")
            shutil.copy2(main_file, backup_file)
            print(f"   ✓ Резервная копия создана: {backup_file}")
        
        # Удаляем старый файл
        if main_file.exists():
            print(f"\n🗑️  Удаление старой версии...")
            os.remove(main_file)
            print(f"   ✓ Старая версия удалена")
        
        # Заменяем файл
        print(f"\n📥 Установка новой версии...")
        shutil.move(str(update_file), str(main_file))
        print(f"   ✓ Новая версия установлена!")
        
        # Удаляем резервную копию
        if backup_file.exists():
            os.remove(backup_file)
        
        print("\n" + "=" * 60)
        print("✅ Обновление успешно установлено!")
        print("=" * 60)
        print("\n🚀 Запуск обновленного приложения...")
        
        # Запускаем обновленное приложение
        os.startfile(str(main_file))
        
    except Exception as e:
        print(f"\n❌ Ошибка при обновлении: {e}")
        
        # Восстанавливаем из резервной копии
        if backup_file.exists() and not main_file.exists():
            print("\n♻️  Восстановление из резервной копии...")
            shutil.copy2(backup_file, main_file)
            print("   ✓ Приложение восстановлено из резервной копии")
        
        time.sleep(5)

if __name__ == "__main__":
    update_application()
