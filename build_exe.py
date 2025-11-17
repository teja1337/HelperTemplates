"""
Скрипт для создания .exe файла с помощью PyInstaller
Запустите: python build_exe.py
"""
import os
import shutil
import subprocess
import sys

def build_exe():
    """Создание исполняемого файла"""
    
    print("=" * 60)
    print("🔨 Начинаю сборку Helper.exe...")
    print("=" * 60)
    
    # Путь к текущей директории
    project_dir = os.path.dirname(os.path.abspath(__file__))
    dist_dir = os.path.join(project_dir, 'dist')
    build_dir = os.path.join(project_dir, 'build')
    
    # Очистка старых файлов
    print("\n📦 Очищаю старые файлы сборки...")
    for dir_path in [dist_dir, build_dir]:
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)
            print(f"   ✓ Удалена папка {dir_path}")
    
    # Команда для PyInstaller
    pyinstaller_cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--onefile',  # Один исполняемый файл
        '--windowed',  # Без консольного окна
        '--name', 'Helper',  # Имя приложения
        '--distpath', dist_dir,
        '--workpath', build_dir,
        '--specpath', project_dir,
        os.path.join(project_dir, 'main.py')
    ]
    
    # Добавляем иконку если она существует
    icon_path = os.path.join(project_dir, 'helper.ico')
    if os.path.exists(icon_path):
        pyinstaller_cmd.insert(5, icon_path)
        pyinstaller_cmd.insert(4, '--icon')
    
    print("\n🔨 Запускаю PyInstaller...")
    print(f"   Команда: {' '.join(pyinstaller_cmd)}\n")
    
    try:
        result = subprocess.run(pyinstaller_cmd, check=True)
        
        if result.returncode == 0:
            exe_path = os.path.join(dist_dir, 'Helper.exe')
            
            if os.path.exists(exe_path):
                print("\n" + "=" * 60)
                print("✅ УСПЕШНО! Helper.exe создан!")
                print("=" * 60)
                print(f"\n📂 Путь к файлу: {exe_path}")
                print(f"📊 Размер файла: {os.path.getsize(exe_path) / (1024*1024):.2f} MB")
                print("\n💡 Вы можете запустить приложение, двойной клик на Helper.exe")
                print("   или скопировать его куда угодно")
                
                return True
            else:
                print("❌ Ошибка: Helper.exe не найден в папке dist")
                return False
    
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Ошибка при сборке: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Непредвиденная ошибка: {e}")
        return False

if __name__ == '__main__':
    success = build_exe()
    sys.exit(0 if success else 1)
