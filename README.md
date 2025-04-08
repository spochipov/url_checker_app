# URL Checker

Приложение для мониторинга доступности веб-сайтов с уведомлениями в Telegram.

## Структура проекта

```
url_checker_app/
├── app/                  # Код приложения
│   ├── main.py           # Основной код приложения
│   └── requirements.txt  # Зависимости Python
│
├── docker/               # Файлы Docker
│   ├── Dockerfile        # Инструкции для сборки Docker-образа
│   ├── docker-compose.yml # Конфигурация Docker Compose
│   └── docker-stack.yml  # Конфигурация для Docker Swarm
│
├── scripts/              # Скрипты
│   ├── deploy.sh         # Скрипт для развертывания на сервере
│   ├── docker_test.sh    # Скрипт для тестирования Docker-конфигурации
│   ├── run_local.sh      # Скрипт для локального запуска без Docker
│   ├── run_tests.sh      # Скрипт для запуска тестов
│   ├── swarm_deploy.sh   # Скрипт для развертывания в Docker Swarm
│   └── update.sh         # Скрипт для обновления приложения
│
├── tests/                # Тесты
│   ├── README.md         # Документация по тестам
│   ├── test_telegram_alert.py # Тесты для функции отправки уведомлений
│   ├── test_retry_session.py  # Тесты для HTTP-сессии
│   ├── test_main.py      # Тесты для основной функции
│   ├── test_integration.py    # Интеграционные тесты
│   └── test_logging.py   # Тесты для логирования
│
├── docs/                 # Документация
│   ├── README.md         # Полная документация
│   ├── TECHNICAL_DOCS.md # Техническая документация
│   └── ARCHITECTURE.md   # Схемы архитектуры
│
├── pytest.ini            # Конфигурация pytest
├── .env.example          # Пример файла с переменными окружения
└── .gitignore            # Файлы, исключенные из системы контроля версий
```

## Быстрый старт

### Локальный запуск

```bash
cp .env.example .env
# Отредактируйте .env файл
chmod +x scripts/run_local.sh
./scripts/run_local.sh
```

### Запуск с Docker

```bash
cp .env.example .env
# Отредактируйте .env файл
chmod +x scripts/docker_test.sh
./scripts/docker_test.sh
```

### Запуск в Docker Swarm

```bash
cp .env.example .env
# Отредактируйте .env файл
chmod +x scripts/swarm_deploy.sh
./scripts/swarm_deploy.sh
```

## Документация

Полная документация доступна в директории [docs/](docs/):

- [Полное руководство](docs/README.md)
- [Техническая документация](docs/TECHNICAL_DOCS.md)
- [Схемы архитектуры](docs/ARCHITECTURE.md)

## Тестирование

Проект включает набор тестов для проверки функциональности:

```bash
# Запуск тестов
./scripts/run_tests.sh
```

Подробная информация о тестах доступна в [tests/README.md](tests/README.md).
