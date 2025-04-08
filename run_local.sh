#!/bin/bash
# Скрипт для локального запуска URL Checker без Docker

# Проверка наличия файла .env
if [ ! -f .env ]; then
    echo "Файл .env не найден. Создаю из примера..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "Создан файл .env из примера. Пожалуйста, отредактируйте его перед запуском."
        exit 1
    else
        echo "Ошибка: файл .env.example не найден. Пожалуйста, создайте файл .env вручную."
        exit 1
    fi
fi

# Проверка наличия Python
if ! command -v python3 &> /dev/null; then
    echo "Python 3 не найден. Пожалуйста, установите Python 3."
    exit 1
fi

# Проверка наличия pip
if ! command -v pip3 &> /dev/null; then
    echo "pip3 не найден. Пожалуйста, установите pip для Python 3."
    exit 1
fi

# Создание виртуального окружения, если его нет
if [ ! -d "venv" ]; then
    echo "Создание виртуального окружения..."
    python3 -m venv venv
fi

# Активация виртуального окружения
echo "Активация виртуального окружения..."
source venv/bin/activate

# Установка зависимостей
echo "Установка зависимостей..."
pip install -r requirements.txt

# Загрузка переменных окружения
echo "Загрузка переменных окружения из .env..."
export $(grep -v '^#' .env | xargs)

# Проверка обязательных переменных
if [ -z "$URL_TO_CHECK" ]; then
    echo "Ошибка: переменная URL_TO_CHECK не задана в файле .env"
    exit 1
fi

# Запуск приложения
echo "Запуск URL Checker..."
echo "Проверяемый URL: $URL_TO_CHECK"
echo "Интервал проверки: ${INTERVAL_SECONDS:-60} секунд"
echo "Для остановки нажмите Ctrl+C"
python main.py
