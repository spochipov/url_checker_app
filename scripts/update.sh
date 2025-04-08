#!/bin/bash
# Скрипт для обновления URL Checker из репозитория

set -e

echo "Обновление URL Checker..."

# Проверка, находимся ли мы в директории проекта
if [ ! -f "app/main.py" ] || [ ! -f "docker/docker-compose.yml" ]; then
    echo "Ошибка: скрипт должен быть запущен из корневой директории проекта URL Checker."
    exit 1
fi

# Проверка наличия git
if ! command -v git &> /dev/null; then
    echo "Git не найден. Пожалуйста, установите Git."
    exit 1
fi

# Проверка, является ли директория git-репозиторием
if [ ! -d ".git" ]; then
    echo "Директория не является git-репозиторием. Невозможно обновить через git."
    echo "Пожалуйста, скачайте последнюю версию вручную."
    exit 1
fi

# Сохранение текущих изменений (если есть)
echo "Сохранение локальных изменений..."
git stash

# Получение последних изменений
echo "Получение последних изменений из репозитория..."
git pull

# Восстановление локальных изменений
echo "Восстановление локальных изменений..."
git stash pop || true  # Игнорируем ошибку, если stash пуст

# Проверка наличия Docker и Docker Compose
if command -v docker &> /dev/null && command -v docker compose &> /dev/null; then
    echo "Обновление Docker-образа..."
    docker compose -f docker/docker-compose.yml build
    
    # Проверка, запущен ли контейнер
    if docker compose -f docker/docker-compose.yml ps | grep -q "url-checker"; then
        echo "Перезапуск контейнера..."
        docker compose -f docker/docker-compose.yml up -d
    else
        echo "Контейнер не запущен. Для запуска выполните: docker compose -f docker/docker-compose.yml up -d"
    fi
else
    echo "Docker или Docker Compose не найдены. Обновление Docker-образа пропущено."
    echo "Для запуска без Docker используйте: ./scripts/run_local.sh"
fi

echo "Обновление завершено."
