
#!/bin/bash
set -e

echo "Переход в директорию проекта..."
cd /home/youruser/url-checker

echo "Обновление образа..."
docker compose -f docker/docker-compose.yml pull

echo "Перезапуск контейнера..."
docker compose -f docker/docker-compose.yml up -d

echo "Готово."
