#!/bin/bash
# Скрипт для запуска тестов URL Checker

# Проверка наличия Python
if ! command -v python3 &> /dev/null; then
    echo "Python 3 не найден. Пожалуйста, установите Python 3."
    exit 1
fi

# Проверка наличия pytest
if ! python3 -c "import pytest" &> /dev/null; then
    echo "Pytest не найден. Устанавливаем..."
    pip install pytest
fi

# Запуск тестов
echo "Запуск тестов..."
python -m pytest -v

# Вывод покрытия кода, если установлен pytest-cov
if python3 -c "import pytest_cov" &> /dev/null; then
    echo "Запуск тестов с покрытием кода..."
    python -m pytest --cov=app tests/
else
    echo "Для анализа покрытия кода установите pytest-cov:"
    echo "pip install pytest-cov"
fi
