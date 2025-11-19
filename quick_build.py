"""
Быстрая сборка Helper.exe и updater.exe БЕЗ установщика
Используется для тестирования, не включает Inno Setup
"""
import os
import sys
import subprocess
import shutil

os.system('chcp 65001 >nul')
sys.stdout.reconfigure(encoding='utf-8')

def build_exe():
    """Быстрая сборка EXE"""
    print("\n" + "="*60)
    print("  БЫСТРАЯ СБОРКА Helper v3.0.0")
    print("="*60 + "\n")
    
    # Запускаем build_exe.py
    print("[*] Сборка Helper.exe и updater.exe...\n")
    result = subprocess.run([sys.executable, "scripts/build_exe.py"], 
                          capture_output=False, text=True)
    
    if result.returncode != 0:
        print("\n❌ Ошибка при сборке EXE")
        return False
    
    # Проверяем наличие файлов
    files = [
        ("dist/Helper.exe", "Основное приложение"),
        ("dist/updater.exe", "Обновлятель"),
    ]
    
    print("\n" + "="*60)
    print("  РЕЗУЛЬТАТЫ СБОРКИ")
    print("="*60 + "\n")
    
    all_exist = True
    for file_path, desc in files:
        if os.path.exists(file_path):
            size_mb = os.path.getsize(file_path) / (1024 * 1024)
            print(f"  ✓ {desc:20} {file_path:25} ({size_mb:.1f} MB)")
        else:
            print(f"  ✗ {desc:20} {file_path:25} (НЕ НАЙДЕН)")
            all_exist = False
    
    print("\n" + "="*60)
    if all_exist:
        print("  ✓ СБОРКА УСПЕШНА!")
    else:
        print("  ✗ НЕКОТОРЫЕ ФАЙЛЫ НЕ СОБРАНЫ")
    print("="*60 + "\n")
    
    return all_exist

if __name__ == "__main__":
    try:
        success = build_exe()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
