"""
Создание GitHub Release v2.0.3 с загрузкой файлов
"""
import requests
import urllib3
from pathlib import Path
from datetime import datetime
import sys

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def create_release(token):
    """Создать релиз и загрузить файлы"""
    
    version = "2.0.3"
    repo = "teja1337/HelperTemplates"
    
    print("=" * 60)
    print(f"🚀 СОЗДАНИЕ GITHUB RELEASE v{version}")
    print("=" * 60)
    
    # 1. Создать релиз
    print(f"\n📦 Создаю релиз v{version}...")
    
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    release_body = f"""# 🎉 Helper v{version} - Красивый интерфейс с иконками!

## ✨ Что нового

### 🎨 Улучшения UI
- ✅ **Иконка в панели задач** - Helper теперь отображается красиво в системной панели
- ✅ **Исправлена видимость окна** - окно больше не исчезает при сворачивании
- ✅ Удалены фреймлесс артефакты для лучшей интеграции с Windows

### 🔧 Исправления и улучшения
- ✅ Версия 2.0.3 с полной иконографикой
- ✅ Все компоненты обновлены и протестированы
- ✅ Готово к регулярному использованию

## 📦 Установка

Скачайте `Helper_Installer.exe` и запустите установщик.

## 🔄 Обновление

- Если у вас v2.0.0 или v2.0.1 - приложение автоматически предложит обновиться
- Если у вас v2.0.2 - обновление до v2.0.3 произойдет автоматически

## 🎯 Что работает
- 💾 Сохранение категорий и шаблонов в %APPDATA%\\Helper
- 🎨 Красивая иконка приложения и установщика
- 🔄 Автоматическая проверка обновлений при запуске
- 📌 Режим "всегда поверх"
- 🔒 Работа через корпоративные прокси

---

📅 **Дата выпуска:** {datetime.now().strftime('%d.%m.%Y %H:%M')}
🔗 **Репозиторий:** https://github.com/teja1337/HelperTemplates
"""
    
    data = {
        "tag_name": f"v{version}",
        "name": f"Helper v{version}",
        "body": release_body,
        "draft": False,
        "prerelease": False
    }
    
    resp = requests.post(
        f'https://api.github.com/repos/{repo}/releases',
        json=data,
        headers=headers,
        verify=False
    )
    
    if resp.status_code not in [200, 201]:
        print(f"❌ Ошибка: {resp.status_code}")
        print(resp.text)
        return False
    
    release_id = resp.json()['id']
    upload_url = resp.json()['upload_url'].split('{')[0]
    
    print(f"✅ Релиз создан! ID: {release_id}")
    print(f"📤 URL для загрузки: {upload_url}")
    
    # 2. Загрузить файлы
    print("\n" + "=" * 60)
    print("📤 ЗАГРУЗКА ФАЙЛОВ")
    print("=" * 60)
    
    files = [
        (Path('dist/Helper.exe'), 'Helper.exe'),
        (Path('dist/updater.exe'), 'updater.exe'),
        (Path('dist/Helper_Installer.exe'), 'Helper_Installer.exe'),
    ]
    
    headers['Content-Type'] = 'application/octet-stream'
    
    for file_path, file_name in files:
        if not file_path.exists():
            print(f"\n⚠️  {file_name} не найден!")
            continue
        
        size_mb = file_path.stat().st_size / (1024 * 1024)
        print(f"\n📤 Загружаю {file_name} ({size_mb:.2f} MB)...")
        
        try:
            with open(file_path, 'rb') as f:
                resp = requests.post(
                    f"{upload_url}?name={file_name}",
                    headers=headers,
                    data=f,
                    verify=False,
                    timeout=600
                )
            
            if resp.status_code in [200, 201]:
                print(f"   ✅ {file_name} загружен!")
            else:
                print(f"   ❌ Ошибка: {resp.status_code}")
                print(resp.text)
                
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 РЕЛИЗ ГОТОВ!")
    print("=" * 60)
    print(f"\n🔗 Ссылка: https://github.com/{repo}/releases/tag/v{version}")
    
    return True

if __name__ == "__main__":
    token = input("Введите GitHub Personal Access Token: ").strip()
    
    if not token:
        print("❌ Токен не указан!")
        sys.exit(1)
    
    success = create_release(token)
    sys.exit(0 if success else 1)
