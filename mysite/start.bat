@echo off
chcp 65001 >nul
title Django Shop - Запуск
color 0A

echo ========================================
echo   Django Shop - Автоматический запуск
echo ========================================
echo.

cd /d "%~dp0"

if not exist venv (
    echo [1/4] Создание виртуального окружения...
    python -m venv venv

    if errorlevel 1 (
        echo.
        echo ОШИБКА: Не удалось создать виртуальное окружение.
        pause
        exit /b 1
    )

    echo       Готово!
) else (
    echo [1/4] Виртуальное окружение уже есть
)

echo.
echo [2/4] Активация окружения...
call venv\Scripts\activate

echo.
echo [3/4] Проверка зависимостей...
pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo ОШИБКА: Не удалось установить зависимости.
    pause
    exit /b 1
)

echo.
echo [4/4] Проверка и применение миграций...
python manage.py migrate

if errorlevel 1 (
    echo.
    echo ОШИБКА: Не удалось выполнить миграции.
    pause
    exit /b 1
)

echo.
echo ========================================
echo   СЕРВЕР ЗАПУЩЕН!
echo   Открой браузер:
echo   http://127.0.0.1:8000
echo ========================================
echo.

python manage.py runserver

pause