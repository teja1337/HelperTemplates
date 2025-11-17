"""
Модуль для автоматического обновления приложения
"""
import requests
import json
import subprocess
import os
import sys
from pathlib import Path

class AppUpdater:
    """Класс для автоматического обновления приложения"""
    
    VERSION_FILE = "version.json"
    REPO_URL = "https://raw.githubusercontent.com/teja1337/HelperTemplates/main/version.json"
    
    @staticmethod
    def get_local_version():
        """Получить локальную версию"""
        try:
            version_path = Path(sys.executable).parent / AppUpdater.VERSION_FILE if getattr(sys, 'frozen', False) else Path(AppUpdater.VERSION_FILE)
            with open(version_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('version', '0.0.0')
        except:
            return '0.0.0'
    
    @staticmethod
    def get_remote_version():
        """Получить версию с GitHub"""
        try:
            response = requests.get(AppUpdater.REPO_URL, timeout=5)
            response.raise_for_status()
            data = response.json()
            return data.get('version', '0.0.0'), data.get('download_url', '')
        except Exception as e:
            print(f"Ошибка при получении версии с GitHub: {e}")
            return None, None
    
    @staticmethod
    def compare_versions(local, remote):
        """Сравнить версии (1.0.0 > 0.9.0)"""
        try:
            local_parts = [int(x) for x in local.split('.')]
            remote_parts = [int(x) for x in remote.split('.')]
            return remote_parts > local_parts
        except:
            return False
    
    @staticmethod
    def download_update(download_url, progress_callback=None):
        """Скачать обновление"""
        try:
            # Определяем путь для сохранения
            if getattr(sys, 'frozen', False):
                save_path = Path(sys.executable).parent / "Helper_update.exe"
            else:
                save_path = Path("Helper_update.exe")
            
            response = requests.get(download_url, stream=True, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size and progress_callback:
                            progress = (downloaded / total_size * 100)
                            progress_callback(progress)
            
            return True, str(save_path)
        except Exception as e:
            print(f"Ошибка при скачивании: {e}")
            return False, None
    
    @staticmethod
    def check_for_updates():
        """Проверить наличие обновлений"""
        local_version = AppUpdater.get_local_version()
        remote_version, download_url = AppUpdater.get_remote_version()
        
        if remote_version and AppUpdater.compare_versions(local_version, remote_version):
            return True, remote_version, download_url
        
        return False, local_version, None
    
    @staticmethod
    def install_update(root_window):
        """Установить обновление через updater.exe"""
        try:
            # Закрываем главное окно
            root_window.quit()
            root_window.destroy()
            
            # Определяем путь к updater.exe
            if getattr(sys, 'frozen', False):
                updater_path = Path(sys.executable).parent / "updater.exe"
            else:
                updater_path = Path("dist") / "updater.exe"
            
            # Запускаем updater.exe
            if updater_path.exists():
                subprocess.Popen([str(updater_path)])
            else:
                print("updater.exe не найден!")
            
            sys.exit()
        except Exception as e:
            print(f"Ошибка при установке обновления: {e}")
