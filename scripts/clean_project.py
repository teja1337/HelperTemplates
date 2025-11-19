"""
Скрипт для удаления неиспользуемых файлов и очистки проекта
"""
import os
import shutil
from pathlib import Path

def clean_project():
    """Удаляет неиспользуемые файлы и директории"""
    
    base_dir = Path(__file__).parent
    
    # Тестовые файлы
    test_files = [
        'test_stats.py',
        'test_stats_final.py',
        'test_stats_integration.py',
        'test_increment_debug.py',
        'test_top.py',
        'check_icon.py',
        'create_icon.py',
        'add_icons.ps1',
        'ICON_REPLACEMENT_GUIDE.md',
    ]
    
    # Неиспользуемые скрипты
    unused_scripts = [
        'scripts/test_manager.py',
        'scripts/test_ui_fixes.py',
        'scripts/test_updater.py',
        'scripts/test_version.py',
        'scripts/check_release.py',
        'scripts/check_v2_release.py',
        'scripts/check_v2.0.2.py',
        'scripts/list_releases.py',
        'scripts/upload_remaining.py',
        'scripts/upload_to_release.py',
        'scripts/quick_deploy.py',
        'scripts/deploy.py',
        'scripts/auto_deploy.py',
        'scripts/create_release_v203.py',
    ]
    
    # Неиспользуемые модули
    unused_modules = [
        'styles/theme.py',
    ]
    
    # Временные директории
    temp_dirs = [
        'test_update',
        '__pycache__',
        'build',
        'scripts/build',
        'scripts/__pycache__',
        'config/__pycache__',
        'models/__pycache__',
        'views/__pycache__',
        'utils/__pycache__',
        'styles/__pycache__',
    ]
    
    deleted_files = 0
    deleted_dirs = 0
    errors = []
    
    print("🗑️  ОЧИСТКА ПРОЕКТА")
    print("=" * 60)
    
    # Удаление файлов
    all_files = test_files + unused_scripts + unused_modules
    for file_path in all_files:
        full_path = base_dir / file_path
        if full_path.exists():
            try:
                os.remove(full_path)
                print(f"✅ Удалён: {file_path}")
                deleted_files += 1
            except Exception as e:
                print(f"❌ Ошибка при удалении {file_path}: {e}")
                errors.append((file_path, str(e)))
        else:
            print(f"⏭️  Пропущен (не найден): {file_path}")
    
    print("\n" + "=" * 60)
    print("🗂️  ОЧИСТКА ДИРЕКТОРИЙ")
    print("=" * 60)
    
    # Удаление директорий
    for dir_path in temp_dirs:
        full_path = base_dir / dir_path
        if full_path.exists() and full_path.is_dir():
            try:
                shutil.rmtree(full_path)
                print(f"✅ Удалена директория: {dir_path}")
                deleted_dirs += 1
            except Exception as e:
                print(f"❌ Ошибка при удалении {dir_path}: {e}")
                errors.append((dir_path, str(e)))
        else:
            print(f"⏭️  Пропущена (не найдена): {dir_path}")
    
    # Итоги
    print("\n" + "=" * 60)
    print("📊 ИТОГИ ОЧИСТКИ")
    print("=" * 60)
    print(f"✅ Удалено файлов: {deleted_files}")
    print(f"✅ Удалено директорий: {deleted_dirs}")
    
    if errors:
        print(f"\n⚠️  Ошибок: {len(errors)}")
        for path, error in errors:
            print(f"  - {path}: {error}")
    else:
        print("\n🎉 Очистка завершена без ошибок!")
    
    return deleted_files, deleted_dirs, errors


if __name__ == "__main__":
    print("\n⚠️  ВНИМАНИЕ: Этот скрипт удалит неиспользуемые файлы!")
    print("Убедитесь что у вас есть backup или git commit.\n")
    
    response = input("Продолжить? (y/N): ").strip().lower()
    
    if response == 'y':
        clean_project()
    else:
        print("❌ Очистка отменена.")
