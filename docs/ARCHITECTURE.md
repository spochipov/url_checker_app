# Схема работы приложения URL Checker

## Общая архитектура

```mermaid
graph TD
    subgraph "Конфигурация"
        ENV[".env файл"] --> CONFIG["Переменные окружения"]
    end

    subgraph "Основной процесс"
        MAIN["main.py"] --> INIT["Инициализация"]
        INIT --> LOGGER["Настройка логирования"]
        INIT --> SESSION["Создание HTTP-сессии с retry"]
        SESSION --> LOOP["Основной цикл"]
        
        LOOP --> CHECK["Проверка URL"]
        CHECK --> ANALYZE["Анализ ответа"]
        ANALYZE --> |"Успех (200)"| LOG_SUCCESS["Логирование успеха"]
        ANALYZE --> |"Ошибка (!= 200)"| LOG_ERROR["Логирование ошибки"]
        LOG_ERROR --> NOTIFY["Отправка уведомления"]
        
        LOG_SUCCESS --> SLEEP["Ожидание (interval)"]
        NOTIFY --> SLEEP
        SLEEP --> CHECK
    end
    
    CONFIG --> MAIN
    
    subgraph "Уведомления"
        NOTIFY --> TELEGRAM["Telegram API"]
    end
    
    subgraph "Логирование"
        LOG_SUCCESS --> LOG_FILE["logs/app.log"]
        LOG_ERROR --> LOG_FILE
        LOG_SUCCESS --> CONSOLE["Консоль"]
        LOG_ERROR --> CONSOLE
    end
end
</mermaid>

## Варианты развертывания

```mermaid
graph TD
    APP["URL Checker"] --> LOCAL["Локальный запуск"]
    APP --> DOCKER["Docker"]
    APP --> SWARM["Docker Swarm"]
    
    subgraph "Локальный запуск"
        LOCAL --> PYTHON["Python + venv"]
        PYTHON --> RUN_LOCAL["run_local.sh"]
    end
    
    subgraph "Docker"
        DOCKER --> COMPOSE["Docker Compose"]
        COMPOSE --> DOCKER_TEST["docker_test.sh"]
        COMPOSE --> DEPLOY["deploy.sh"]
    end
    
    subgraph "Docker Swarm"
        SWARM --> STACK["Docker Stack"]
        STACK --> SWARM_DEPLOY["swarm_deploy.sh"]
        SWARM_DEPLOY --> REPLICAS["Множественные реплики"]
    end
    
    UPDATE["update.sh"] --> LOCAL
    UPDATE --> DOCKER
    UPDATE --> SWARM
</mermaid>

## Процесс мониторинга и уведомлений

```mermaid
sequenceDiagram
    participant App as URL Checker
    participant Target as Целевой URL
    participant Logs as Логи
    participant Telegram as Telegram API
    
    loop Каждые interval секунд
        App->>Target: HTTP GET запрос
        alt Успешный ответ (200)
            Target->>App: Статус 200
            App->>Logs: Логирование успеха
        else Ошибка (!= 200)
            Target->>App: Ошибка (4xx/5xx) или таймаут
            App->>Logs: Логирование ошибки
            App->>Telegram: Отправка уведомления
            Telegram-->>App: Подтверждение отправки
        end
    end
</mermaid>

## Архитектура Docker Swarm

```mermaid
graph TD
    subgraph "Docker Swarm Кластер"
        subgraph "Manager Node"
            MANAGER["Swarm Manager"]
            MANAGER --> DEPLOY["Развертывание стека"]
            DEPLOY --> SERVICES["Управление сервисами"]
        end
        
        subgraph "Worker Nodes"
            WORKER1["Worker Node 1"]
            WORKER2["Worker Node 2"]
            WORKER3["Worker Node 3"]
        end
        
        SERVICES --> WORKER1
        SERVICES --> WORKER2
        SERVICES --> WORKER3
        
        subgraph "URL Checker Service"
            WORKER1 --> REPLICA1["Реплика 1"]
            WORKER2 --> REPLICA2["Реплика 2"]
            WORKER3 --> REPLICA3["Реплика 3"]
        end
    end
    
    REGISTRY["Docker Registry"] --> DEPLOY
    
    subgraph "Внешние системы"
        REPLICA1 --> URL["Целевой URL"]
        REPLICA2 --> URL
        REPLICA3 --> URL
        
        REPLICA1 --> TELEGRAM["Telegram API"]
        REPLICA2 --> TELEGRAM
        REPLICA3 --> TELEGRAM
    end
</mermaid>

## Процесс развертывания в Docker Swarm

```mermaid
sequenceDiagram
    participant User as Пользователь
    participant Script as swarm_deploy.sh
    participant Docker as Docker CLI
    participant Registry as Docker Registry
    participant Swarm as Docker Swarm
    
    User->>Script: Запуск ./swarm_deploy.sh
    Script->>Docker: Проверка Swarm режима
    alt Swarm не активен
        Script->>Docker: docker swarm init
        Docker-->>Script: Swarm инициализирован
    end
    
    Script->>Docker: Сборка образа
    Docker-->>Script: Образ собран
    
    alt Внешний реестр
        Script->>Docker: Отправка образа в реестр
        Docker->>Registry: docker push
        Registry-->>Docker: Образ отправлен
    end
    
    Script->>Docker: Развертывание стека
    Docker->>Swarm: docker stack deploy
    Swarm-->>Docker: Стек развернут
    Docker-->>Script: Результат развертывания
    Script-->>User: Информация о развернутом стеке
</mermaid>
