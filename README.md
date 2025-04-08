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
│   ├── swarm_deploy.sh   # Скрипт для развертывания в Docker Swarm
│   └── update.sh         # Скрипт для обновления приложения
│
├── docs/                 # Документация
│   ├── README.md         # Полная документация
│   ├── TECHNICAL_DOCS.md # Техническая документация
│   └── ARCHITECTURE.md   # Схемы архитектуры
│
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
