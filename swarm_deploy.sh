#!/bin/bash
# Скрипт для развертывания URL Checker в Docker Swarm

set -e

# Проверка, запущен ли Docker в режиме Swarm
if ! docker info | grep -q "Swarm: active"; then
    echo "Docker не запущен в режиме Swarm. Инициализируем Swarm..."
    docker swarm init || {
        echo "Не удалось инициализировать Swarm. Пожалуйста, выполните 'docker swarm init' вручную."
        exit 1
    }
fi

# Параметры по умолчанию
STACK_NAME="url-checker"
DOCKER_REGISTRY="localhost"
TAG="latest"
REPLICAS=1

# Парсинг аргументов командной строки
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        --stack-name)
            STACK_NAME="$2"
            shift 2
            ;;
        --registry)
            DOCKER_REGISTRY="$2"
            shift 2
            ;;
        --tag)
            TAG="$2"
            shift 2
            ;;
        --replicas)
            REPLICAS="$2"
            shift 2
            ;;
        --help)
            echo "Использование: $0 [опции]"
            echo "Опции:"
            echo "  --stack-name NAME    Имя стека (по умолчанию: url-checker)"
            echo "  --registry URL       URL Docker-реестра (по умолчанию: localhost)"
            echo "  --tag TAG            Тег образа (по умолчанию: latest)"
            echo "  --replicas N         Количество реплик (по умолчанию: 1)"
            echo "  --help               Показать эту справку"
            exit 0
            ;;
        *)
            echo "Неизвестная опция: $key"
            echo "Используйте --help для получения справки"
            exit 1
            ;;
    esac
done

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

# Проверка обязательных переменных в .env
URL_TO_CHECK=$(grep -v '^#' .env | grep URL_TO_CHECK | cut -d '=' -f2)
if [ -z "$URL_TO_CHECK" ]; then
    echo "Ошибка: переменная URL_TO_CHECK не задана в файле .env"
    exit 1
fi

# Сборка образа
echo "Сборка Docker-образа..."
docker build -t ${DOCKER_REGISTRY}/url-checker:${TAG} .

# Если указан внешний реестр, отправляем образ
if [ "$DOCKER_REGISTRY" != "localhost" ]; then
    echo "Отправка образа в реестр ${DOCKER_REGISTRY}..."
    docker push ${DOCKER_REGISTRY}/url-checker:${TAG}
fi

# Экспорт переменных для docker-stack.yml
export DOCKER_REGISTRY
export TAG
export REPLICAS

# Развертывание стека
echo "Развертывание стека ${STACK_NAME}..."
docker stack deploy -c docker-stack.yml ${STACK_NAME}

echo "Стек ${STACK_NAME} успешно развернут."
echo "Для просмотра сервисов выполните: docker service ls"
echo "Для просмотра логов выполните: docker service logs ${STACK_NAME}_url-checker"
echo "Для удаления стека выполните: docker stack rm ${STACK_NAME}"
