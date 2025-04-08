# Техническая документация URL Checker

## Структура проекта

```
url_checker_app/
├── main.py                # Основной код приложения
├── requirements.txt       # Зависимости Python
├── Dockerfile             # Инструкции для сборки Docker-образа
├── docker-compose.yml     # Конфигурация Docker Compose
├── docker-stack.yml       # Конфигурация для Docker Swarm
├── deploy.sh              # Скрипт для развертывания на сервере
├── swarm_deploy.sh        # Скрипт для развертывания в Docker Swarm
├── run_local.sh           # Скрипт для локального запуска без Docker
├── docker_test.sh         # Скрипт для тестирования Docker-конфигурации
├── update.sh              # Скрипт для обновления приложения
├── .env.example           # Пример файла с переменными окружения
├── .gitignore             # Файлы, исключенные из системы контроля версий
├── README.md              # Общая документация
├── TECHNICAL_DOCS.md      # Техническая документация
└── logs/                  # Директория для логов (создается автоматически)
    └── app.log            # Файл логов
```

## Компоненты приложения

### main.py

Основной файл приложения содержит следующие компоненты:

#### 1. Настройка логирования

```python
# Настройка логгера с ротацией
log_dir = "logs"
log_file_path = os.path.join(log_dir, "app.log")
os.makedirs(log_dir, exist_ok=True)

logger = logging.getLogger()
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

file_handler = RotatingFileHandler(log_file_path, maxBytes=5*1024*1024, backupCount=3)
file_handler.setFormatter(formatter)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)
```

Эта часть кода настраивает систему логирования с использованием:
- `RotatingFileHandler` для ротации логов (максимальный размер файла 5 МБ, хранятся 3 последних файла)
- `StreamHandler` для вывода логов в консоль
- Формат логов: `время - уровень - сообщение`

#### 2. Отправка уведомлений в Telegram

```python
def send_telegram_alert(message: str):
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not bot_token or not chat_id:
        logger.warning("Telegram токен или chat_id не заданы, сообщение не отправлено.")
        return

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message
    }
    try:
        resp = requests.post(url, json=payload, timeout=10)
        if resp.status_code != 200:
            logger.warning(f"Не удалось отправить сообщение в Telegram. Код ответа: {resp.status_code}")
    except Exception as e:
        logger.error(f"Ошибка при отправке сообщения в Telegram: {e}")
```

Функция `send_telegram_alert`:
- Получает токен бота и ID чата из переменных окружения
- Отправляет POST-запрос к API Telegram
- Обрабатывает ошибки и логирует их
- Имеет таймаут 10 секунд для запроса

#### 3. HTTP-сессия с автоматическими повторами

```python
def get_retry_session():
    session = requests.Session()
    retries = Retry(total=3, backoff_factor=2, status_forcelist=[500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session
```

Функция `get_retry_session`:
- Создает сессию requests с настройкой автоматических повторов
- Настраивает 3 повторных попытки при ошибках
- Использует экспоненциальную задержку между попытками (backoff_factor=2)
- Повторяет запросы при получении статус-кодов 500, 502, 503, 504

#### 4. Основная функция

```python
def main():
    url = os.getenv("URL_TO_CHECK")
    interval = int(os.getenv("INTERVAL_SECONDS", "60"))

    if not url:
        logger.error("Переменная окружения URL_TO_CHECK не задана.")
        return

    logger.info(f"Начинаем проверку URL: {url} каждые {interval} секунд")

    session = get_retry_session()

    while True:
        try:
            response = session.get(url, timeout=10)
            if response.status_code != 200:
                msg = f"Ошибка: получен статус-код {response.status_code} от {url}"
                logger.error(msg)
                send_telegram_alert(msg)
            else:
                logger.info(f"Успешный запрос: статус 200 от {url}")
        except Exception as e:
            msg = f"Ошибка при выполнении запроса: {e}"
            logger.error(msg)
            send_telegram_alert(msg)
        
        time.sleep(interval)
```

Функция `main`:
- Получает URL для проверки и интервал из переменных окружения
- Создает HTTP-сессию с настройкой повторов
- Запускает бесконечный цикл проверки URL
- Отправляет уведомления в Telegram при ошибках
- Логирует результаты каждой проверки
- Использует таймаут 10 секунд для HTTP-запросов

### requirements.txt

Файл содержит список зависимостей Python:
```
requests
```

Единственная внешняя зависимость - библиотека `requests` для выполнения HTTP-запросов.

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py main.py

CMD ["python", "main.py"]
```

Dockerfile описывает:
- Базовый образ: Python 3.11 (slim-версия)
- Рабочую директорию: `/app`
- Установку зависимостей из requirements.txt
- Копирование основного файла приложения
- Команду запуска: `python main.py`

### docker-compose.yml

```yaml
version: '3.8'

services:
  url-checker:
    build: .
    environment:
      - URL_TO_CHECK=${URL_TO_CHECK}
      - INTERVAL_SECONDS=${INTERVAL_SECONDS}
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
      - TELEGRAM_CHAT_ID=${TELEGRAM_CHAT_ID}
    env_file:
      - .env
    healthcheck:
      test: ["CMD", "curl", "-f", "${URL_TO_CHECK}"]
      interval: 30s
      timeout: 5s
      retries: 3
```

Файл docker-compose.yml:
- Определяет сервис `url-checker`
- Настраивает переменные окружения из файла `.env`
- Настраивает проверку работоспособности (healthcheck) с использованием curl
- Интервал проверки работоспособности: 30 секунд
- Таймаут проверки: 5 секунд
- Количество повторных попыток: 3

### docker-stack.yml

```yaml
version: '3.8'

services:
  url-checker:
    image: ${DOCKER_REGISTRY:-localhost}/url-checker:${TAG:-latest}
    environment:
      - URL_TO_CHECK=${URL_TO_CHECK}
      - INTERVAL_SECONDS=${INTERVAL_SECONDS}
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
      - TELEGRAM_CHAT_ID=${TELEGRAM_CHAT_ID}
    env_file:
      - .env
    healthcheck:
      test: ["CMD", "curl", "-f", "${URL_TO_CHECK}"]
      interval: 30s
      timeout: 5s
      retries: 3
    deploy:
      mode: replicated
      replicas: ${REPLICAS:-1}
      update_config:
        parallelism: 1
        delay: 10s
        order: start-first
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
        window: 120s
      resources:
        limits:
          cpus: '0.50'
          memory: 256M
        reservations:
          cpus: '0.25'
          memory: 128M
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
    networks:
      - url-checker-network

networks:
  url-checker-network:
    driver: overlay
```

Файл docker-stack.yml:
- Определяет сервис `url-checker` для развертывания в Docker Swarm
- Использует предварительно собранный образ из реестра
- Настраивает переменные окружения из файла `.env`
- Настраивает проверку работоспособности (healthcheck)
- Определяет параметры развертывания (deploy):
  - Режим репликации с настраиваемым количеством реплик
  - Стратегию обновления с параллельностью 1 и задержкой 10 секунд
  - Политику перезапуска при сбоях
  - Ограничения и резервирование ресурсов (CPU и память)
- Настраивает логирование с ротацией (максимальный размер 10 МБ, хранятся 3 последних файла)
- Создает overlay-сеть для коммуникации между сервисами

### Вспомогательные скрипты

#### deploy.sh

```bash
#!/bin/bash
set -e

echo "Переход в директорию проекта..."
cd /home/youruser/url-checker

echo "Обновление образа..."
docker compose pull

echo "Перезапуск контейнера..."
docker compose up -d

echo "Готово."
```

Скрипт deploy.sh:
- Переходит в директорию проекта на сервере
- Обновляет Docker-образ
- Перезапускает контейнер в фоновом режиме
- Использует флаг `set -e` для остановки выполнения при ошибках

#### run_local.sh

```bash
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
```

Скрипт run_local.sh:
- Проверяет наличие файла .env и создает его из примера при необходимости
- Проверяет наличие Python и pip
- Создает и активирует виртуальное окружение
- Устанавливает зависимости
- Загружает переменные окружения из файла .env
- Проверяет наличие обязательных переменных
- Запускает приложение

#### docker_test.sh

```bash
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
docker compose build

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
docker compose up -d

# Вывод логов
echo "Вывод логов контейнера (для остановки нажмите Ctrl+C):"
docker compose logs -f

# Примечание: после нажатия Ctrl+C скрипт продолжит выполнение
echo "Контейнер продолжает работать в фоновом режиме."
echo "Для остановки контейнера выполните: docker compose down"
```

Скрипт docker_test.sh:
- Проверяет наличие Docker и Docker Compose
- Проверяет наличие файла .env и создает его из примера при необходимости
- Собирает Docker-образ
- Проверяет наличие обязательных переменных окружения
- Запускает контейнер в фоновом режиме
- Выводит логи контейнера

#### swarm_deploy.sh

```bash
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
```

Скрипт swarm_deploy.sh:
- Проверяет, запущен ли Docker в режиме Swarm, и инициализирует его при необходимости
- Принимает параметры командной строки для настройки развертывания:
  - Имя стека
  - URL Docker-реестра
  - Тег образа
  - Количество реплик
- Проверяет наличие файла .env и создает его из примера при необходимости
- Проверяет наличие обязательных переменных окружения
- Собирает Docker-образ
- Отправляет образ в реестр, если указан внешний реестр
- Экспортирует переменные для docker-stack.yml
- Развертывает стек в Docker Swarm
- Выводит информацию о командах для управления стеком

#### update.sh

```bash
#!/bin/bash
# Скрипт для обновления URL Checker из репозитория

set -e

echo "Обновление URL Checker..."

# Проверка, находимся ли мы в директории проекта
if [ ! -f "main.py" ] || [ ! -f "docker-compose.yml" ]; then
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
    docker compose build
    
    # Проверка, запущен ли контейнер
    if docker compose ps | grep -q "url-checker"; then
        echo "Перезапуск контейнера..."
        docker compose up -d
    else
        echo "Контейнер не запущен. Для запуска выполните: docker compose up -d"
    fi
else
    echo "Docker или Docker Compose не найдены. Обновление Docker-образа пропущено."
    echo "Для запуска без Docker используйте: ./run_local.sh"
fi

echo "Обновление завершено."
```

Скрипт update.sh:
- Проверяет, находимся ли мы в директории проекта
- Проверяет наличие git и является ли директория git-репозиторием
- Сохраняет локальные изменения
- Получает последние изменения из репозитория
- Восстанавливает локальные изменения
- Обновляет Docker-образ и перезапускает контейнер при необходимости

### Конфигурационные файлы

#### .env.example

```
# URL Checker - Пример файла конфигурации
# Переименуйте этот файл в .env для использования

# Обязательные параметры
# URL, который нужно проверять
URL_TO_CHECK=https://example.com

# Опциональные параметры
# Интервал между проверками в секундах (по умолчанию 60)
INTERVAL_SECONDS=60

# Настройки Telegram для уведомлений (опционально)
# Получите токен бота через @BotFather
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
# Получите ID чата через @userinfobot
TELEGRAM_CHAT_ID=your_telegram_chat_id

# Дополнительные параметры (для расширенной функциональности)
# Порог времени отклика в секундах для предупреждений
# RESPONSE_TIME_THRESHOLD=2.0

# Ожидаемый текст на странице (для проверки содержимого)
# EXPECTED_TEXT=Welcome to Example

# Настройки для email-уведомлений (если реализовано)
# SMTP_SERVER=smtp.gmail.com
# SMTP_PORT=587
# SMTP_USER=your_email@gmail.com
# SMTP_PASSWORD=your_app_password
# EMAIL_RECIPIENT=recipient@example.com
```

Файл .env.example:
- Содержит примеры всех поддерживаемых переменных окружения
- Включает комментарии с описанием каждой переменной
- Содержит примеры для расширенной функциональности

#### .gitignore

```
# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Logs
logs/
*.log

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Docker
.dockerignore

# IDE
.idea/
.vscode/
*.swp
*.swo
*~

# OS specific
.DS_Store
Thumbs.db
```

Файл .gitignore:
- Исключает файл .env с конфиденциальными данными
- Исключает директорию logs и файлы логов
- Исключает файлы Python, Docker, IDE и OS-специфичные файлы

## Развертывание в Docker Swarm

### Подготовка к развертыванию

Для развертывания приложения в Docker Swarm необходимо:

1. Инициализировать Docker Swarm на хосте:
   ```bash
   docker swarm init
   ```
   
   Или присоединиться к существующему кластеру:
   ```bash
   docker swarm join --token <token> <manager-ip>:<port>
   ```

2. Настроить Docker-реестр для хранения образов (опционально):
   - Использовать публичный реестр (Docker Hub)
   - Настроить приватный реестр
   - Использовать локальный реестр для тестирования:
     ```bash
     docker run -d -p 5000:5000 --restart=always --name registry registry:2
     ```

### Процесс развертывания

Процесс развертывания в Docker Swarm включает следующие шаги:

1. Сборка Docker-образа
2. Отправка образа в реестр (если используется внешний реестр)
3. Развертывание стека с помощью `docker stack deploy`

Скрипт `swarm_deploy.sh` автоматизирует этот процесс.

### Масштабирование и управление

Docker Swarm позволяет легко масштабировать сервисы:

```bash
# Увеличение количества реплик
docker service scale url-checker_url-checker=5

# Обновление сервиса
docker service update --image ${DOCKER_REGISTRY}/url-checker:${NEW_TAG} url-checker_url-checker
```

### Мониторинг сервисов

Для мониторинга сервисов в Docker Swarm используйте:

```bash
# Просмотр всех сервисов
docker service ls

# Просмотр задач сервиса
docker service ps url-checker_url-checker

# Просмотр логов сервиса
docker service logs url-checker_url-checker
```

## Алгоритм работы приложения

1. Приложение загружает конфигурацию из переменных окружения
2. Настраивает систему логирования
3. Создает HTTP-сессию с настройкой автоматических повторов
4. Запускает бесконечный цикл:
   - Отправляет HTTP-запрос к указанному URL
   - Проверяет статус-код ответа
   - Логирует результат
   - При ошибке отправляет уведомление в Telegram
   - Ждет указанный интервал времени
   - Повторяет цикл

## Обработка ошибок

Приложение обрабатывает следующие типы ошибок:

1. **Ошибки HTTP-запросов**:
   - Неуспешные статус-коды (не 200)
   - Таймауты соединения
   - Ошибки DNS
   - Другие сетевые ошибки

2. **Ошибки конфигурации**:
   - Отсутствие обязательных переменных окружения
   - Некорректные значения переменных

3. **Ошибки отправки уведомлений**:
   - Проблемы с API Telegram
   - Отсутствие токена или ID чата

## Рекомендации по расширению функциональности

### 1. Добавление поддержки других методов уведомлений

Для добавления поддержки email-уведомлений:

```python
def send_email_alert(message: str):
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    recipient = os.getenv("EMAIL_RECIPIENT")
    
    if not all([smtp_server, smtp_user, smtp_password, recipient]):
        logger.warning("Не все параметры SMTP настроены, email не отправлен.")
        return
        
    try:
        import smtplib
        from email.message import EmailMessage
        
        msg = EmailMessage()
        msg.set_content(message)
        msg["Subject"] = "URL Checker Alert"
        msg["From"] = smtp_user
        msg["To"] = recipient
        
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(msg)
        server.quit()
        
        logger.info(f"Email-уведомление отправлено на {recipient}")
    except Exception as e:
        logger.error(f"Ошибка при отправке email: {e}")
```

### 2. Проверка содержимого страницы

Для проверки наличия определенного текста на странице:

```python
def check_page_content(response, expected_text):
    if expected_text and expected_text in response.text:
        return True
    return False

# В основном цикле:
expected_text = os.getenv("EXPECTED_TEXT")
response = session.get(url, timeout=10)
if response.status_code == 200:
    if expected_text and not check_page_content(response, expected_text):
        msg = f"Ошибка: ожидаемый текст не найден на странице {url}"
        logger.error(msg)
        send_telegram_alert(msg)
    else:
        logger.info(f"Успешный запрос: статус 200 от {url}")
```

### 3. Метрики и мониторинг

Для добавления метрик времени отклика:

```python
import time

# В основном цикле:
start_time = time.time()
response = session.get(url, timeout=10)
response_time = time.time() - start_time

logger.info(f"Время отклика: {response_time:.2f} секунд от {url}")

# Можно добавить предупреждение при превышении порога:
response_time_threshold = float(os.getenv("RESPONSE_TIME_THRESHOLD", "2.0"))
if response_time > response_time_threshold:
    msg = f"Предупреждение: время отклика {response_time:.2f} секунд превышает порог {response_time_threshold} секунд для {url}"
    logger.warning(msg)
    send_telegram_alert(msg)
```

## Безопасность

### Рекомендации по безопасности

1. **Защита токенов и учетных данных**:
   - Храните токены и пароли только в переменных окружения или файле `.env`
   - Не включайте файл `.env` в систему контроля версий
   - Используйте разные токены для разных окружений (разработка, тестирование, продакшн)

2. **Ограничение доступа**:
   - Ограничьте доступ к серверу, на котором запущено приложение
   - Используйте минимальные привилегии для пользователя, от имени которого запускается контейнер

3. **Обновление зависимостей**:
   - Регулярно обновляйте библиотеку requests и базовый образ Python
   - Используйте инструменты для сканирования уязвимостей в зависимостях

## Производительность

Приложение имеет минимальные требования к ресурсам:
- Память: ~50-100 МБ
- CPU: минимальная нагрузка
- Диск: минимальное использование (только для логов)

Для мониторинга большого количества URL рекомендуется:
1. Разделить проверки на несколько экземпляров приложения
2. Использовать асинхронные запросы (например, с библиотекой aiohttp)
3. Настроить более эффективное хранение и ротацию логов
