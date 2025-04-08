
#!/bin/bash
set -e

echo "Переход в директорию проекта..."
cd /home/youruser/url-checker

echo "Обновление образа..."
docker compose pull

echo "Перезапуск контейнера..."
docker compose up -d

echo "Готово."
