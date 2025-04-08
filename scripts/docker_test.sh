#!/bin/bash
# Скрипт для тестирования Docker-конфигурации URL Checker

# Проверка наличия Docker
if ! command -v docker &> /dev/null; then
    echo "Docker не найден. Пожалуйста, установите Docker."
    exit 1
fi

# Проверка наличия Docker Compose
if ! command -v docker compose &> /dev/null; then
    echo "Docker Compose не найден. Пожалуйста, установите Docker Compose."
    exit 1
fi

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

# Сборка Docker-образа
echo "Сборка Docker-образа..."
docker compose -f docker/docker-compose.yml build

# Проверка переменных окружения
echo "Проверка переменных окружения..."
URL_TO_CHECK=$(grep -v '^#' .env | grep URL_TO_CHECK | cut -d '=' -f2)
if [ -z "$URL_TO_CHECK" ]; then
    echo "Ошибка: переменная URL_TO_CHECK не задана в файле .env"
    exit 1
fi

echo "Проверяемый URL: $URL_TO_CHECK"

# Запуск контейнера в фоновом режиме
echo "Запуск контейнера..."
docker compose -f docker/docker-compose.yml up -d

# Вывод логов
echo "Вывод логов контейнера (для остановки нажмите Ctrl+C):"
docker compose -f docker/docker-compose.yml logs -f

# Примечание: после нажатия Ctrl+C скрипт продолжит выполнение
echo "Контейнер продолжает работать в фоновом режиме."
echo "Для остановки контейнера выполните: docker compose -f docker/docker-compose.yml down"
