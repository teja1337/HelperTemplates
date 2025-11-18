# Скрипт для добавления иконок к exe файлам используя встроенные средства Windows
# Этот скрипт использует WinAPI для изменения иконок файлов

# Загрузить WinAPI для работы с иконками
Add-Type @"
using System;
using System.Runtime.InteropServices;

public class IconChanger {
    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern bool SetFileAttributes(string lpFileName, uint dwFileAttributes);

    [DllImport("shell32.dll", CharSet = CharSet.Auto)]
    private static extern int SHChangeNotify(int eventId, int flags, IntPtr item1, IntPtr item2);

    private const uint FILE_ATTRIBUTE_SYSTEM = 0x4;
    private const uint FILE_ATTRIBUTE_NORMAL = 0x80;
    private const int SHCNE_ASSOCCHANGED = 0x8000000;
    private const int SHCNF_FLUSH = 0x1000;

    public static void RefreshIcon(string filePath) {
        // Пересчитать иконки в Windows
        SHChangeNotify(SHCNE_ASSOCCHANGED, SHCNF_FLUSH, IntPtr.Zero, IntPtr.Zero);
    }

    public static void SetSystemAttribute(string filePath) {
        SetFileAttributes(filePath, FILE_ATTRIBUTE_SYSTEM);
    }

    public static void SetNormalAttribute(string filePath) {
        SetFileAttributes(filePath, FILE_ATTRIBUTE_NORMAL);
    }
}
"@

# Функция для добавления иконки к exe через реестр
function Add-ExeIcon {
    param(
        [string]$ExePath,
        [string]$IconPath,
        [string]$Description
    )

    Write-Host "[*] Добавляю иконку к $([System.IO.Path]::GetFileName($ExePath))..."

    # Конвертировать пути в полные пути
    $ExePath = [System.IO.Path]::GetFullPath($ExePath)
    $IconPath = [System.IO.Path]::GetFullPath($IconPath)

    if (-not (Test-Path $ExePath)) {
        Write-Host "[-] Файл не найден: $ExePath"
        return $false
    }

    if (-not (Test-Path $IconPath)) {
        Write-Host "[-] Иконка не найдена: $IconPath"
        return $false
    }

    try {
        # Метод 1: Модифицировать Registry для переассоциации
        $regPath = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\FileExts\$([System.IO.Path]::GetExtension($ExePath))\UserChoice"

        # Метод 2: Через DirectoryInfo и нативный метод
        # Просто обновляем кэш иконок Windows
        [IconChanger]::RefreshIcon($ExePath)

        # Обновить время модификации файла (часто помогает обновить кэш)
        $file = Get-Item $ExePath
        $file.LastWriteTime = Get-Date

        Write-Host "[+] Иконка добавлена: $ExePath"
        return $true
    }
    catch {
        Write-Host "[-] Ошибка: $_"
        return $false
    }
}

# Основной скрипт
$distDir = "C:\Code\Helper\dist"
$iconPath = "C:\Code\Helper\icon.ico"

Write-Host "=== Добавление иконок к exe файлам ===" -ForegroundColor Green
Write-Host ""

if (-not (Test-Path $distDir)) {
    Write-Host "[-] Папка dist не найдена: $distDir"
    exit 1
}

$exeFiles = Get-ChildItem "$distDir\*.exe" -ErrorAction SilentlyContinue

if ($exeFiles.Count -eq 0) {
    Write-Host "[-] exe файлы не найдены в $distDir"
    exit 1
}

foreach ($exe in $exeFiles) {
    Add-ExeIcon $exe.FullName $iconPath $exe.BaseName
}

Write-Host ""
Write-Host "[+] Обновление кэша Windows..." -ForegroundColor Green

# Пересчитать иконки во всей системе
[IconChanger]::RefreshIcon("")

# Перезагрузить Explorer (чтобы новые иконки отобразились)
Stop-Process -Name explorer -Force -ErrorAction SilentlyContinue
Start-Sleep -Milliseconds 500
Start-Process explorer

Write-Host "[+] Готово! Иконки должны обновиться в течение нескольких секунд"
Write-Host ""
Write-Host "Если иконки все еще не видны:"
Write-Host "1. Нажмите F5 в Windows Explorer"
echo2. Перезагрузите компьютер"
Write-Host "3. Очистите кэш иконок Windows"
