"""
Полная сборка Helper: EXE + Установщик
Запуск: python build_all.py
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path

# Установка кодировки
os.system('chcp 65001 >nul')
sys.stdout.reconfigure(encoding='utf-8')

def print_header(text):
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def check_inno_setup():
    """Проверка наличия Inno Setup"""
    inno_paths = [
        r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        r"C:\Program Files\Inno Setup 6\ISCC.exe",
    ]
    
    for path in inno_paths:
        if os.path.exists(path):
            return path
    
    print("❌ Inno Setup не найден!")
    print("   Скачайте: https://jrsoftware.org/isdl.php")
    return None

def build_exe():
    """Сборка EXE файлов"""
    print_header("ШАГ 1: Сборка EXE")
    
    # Запускаем build_exe.py
    result = subprocess.run([sys.executable, "scripts/build_exe.py"], 
                          capture_output=False, text=True)
    
    if result.returncode != 0:
        print("❌ Ошибка при сборке EXE")
        return False
    
    # Проверяем наличие файлов
    if not os.path.exists("dist/Helper.exe"):
        print("❌ Helper.exe не найден в dist/")
        return False
    
    if not os.path.exists("dist/updater.exe"):
        print("❌ updater.exe не найден в dist/")
        return False
    
    print("✅ EXE файлы собраны успешно")
    return True

def prepare_installer_files():
    """Подготовка файлов для установщика"""
    print_header("ШАГ 2: Подготовка файлов для установщика")
    
    # Копируем необходимые файлы в build_config
    files_to_copy = [
        ("data/version.json", "build_config/version.json"),
        ("icon.ico", "build_config/icon.ico"),
        ("icon.ico", "build_config/installer_icon.ico"),
    ]
    
    for src, dst in files_to_copy:
        if os.path.exists(src):
            shutil.copy2(src, dst)
            print(f"✓ Скопирован {src} → {dst}")
        else:
            print(f"⚠ Файл не найден: {src}")
    
    print("✅ Файлы подготовлены")
    return True

def build_installer(iscc_path):
    """Сборка установщика"""
    print_header("ШАГ 3: Сборка установщика")
    
    iss_file = "build_config/installer.iss"
    
    if not os.path.exists(iss_file):
        print(f"❌ Скрипт установщика не найден: {iss_file}")
        return False
    
    # Запускаем Inno Setup
    print(f"📦 Компилирую установщик...")
    result = subprocess.run([iscc_path, iss_file], 
                          capture_output=True, text=True, encoding='utf-8', errors='ignore')
    
    if result.returncode != 0:
        print("❌ Ошибка при сборке установщика:")
        print(result.stderr)
        return False
    
    # Проверяем результат
    installer_file = "dist/Helper_Installer.exe"
    if not os.path.exists(installer_file):
        print(f"❌ Установщик не найден: {installer_file}")
        return False
    
    # Показываем размер
    size_mb = os.path.getsize(installer_file) / (1024 * 1024)
    print(f"✅ Установщик создан: {installer_file} ({size_mb:.1f} MB)")
    return True

def show_results():
    """Показать результаты сборки"""
    print_header("РЕЗУЛЬТАТЫ СБОРКИ")
    
    files = [
        ("dist/Helper.exe", "Основное приложение"),
        ("dist/updater.exe", "Обновлятель"),
        ("dist/Helper_Installer.exe", "Установщик"),
    ]
    
    print("\n📦 Созданные файлы:\n")
    for file_path, description in files:
        if os.path.exists(file_path):
            size_mb = os.path.getsize(file_path) / (1024 * 1024)
            print(f"  ✓ {description:25} {file_path:30} ({size_mb:.1f} MB)")
        else:
            print(f"  ✗ {description:25} {file_path:30} (НЕ НАЙДЕН)")
    
    print("\n" + "="*60)
    print("  🎉 СБОРКА ЗАВЕРШЕНА!")
    print("="*60)

def main():
    """Главная функция"""
    print_header("ПОЛНАЯ СБОРКА HELPER v3.0.0")
    
    # Проверяем Inno Setup
    iscc_path = check_inno_setup()
    if not iscc_path:
        print("\n⚠ Будет создан только EXE (без установщика)")
        create_installer = False
    else:
        print(f"✓ Inno Setup найден: {iscc_path}")
        create_installer = True
    
    # Шаг 1: Сборка EXE
    if not build_exe():
        print("\n❌ СБОРКА ПРЕРВАНА")
        sys.exit(1)
    
    # Шаг 2: Подготовка файлов для установщика
    if create_installer:
        if not prepare_installer_files():
            print("\n⚠ Пропускаю создание установщика")
            create_installer = False
    
    # Шаг 3: Сборка установщика
    if create_installer:
        if not build_installer(iscc_path):
            print("\n⚠ Установщик не создан, но EXE готов")
    
    # Показываем результаты
    show_results()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Сборка прервана пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
