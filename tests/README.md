# Тесты для URL Checker

В этой директории находятся тесты для приложения URL Checker.

## Структура тестов

- `test_telegram_alert.py` - тесты для функции отправки уведомлений в Telegram
- `test_retry_session.py` - тесты для функции создания HTTP-сессии с автоматическими повторами
- `test_main.py` - тесты для основной функции приложения
- `test_integration.py` - интеграционные тесты
- `test_logging.py` - тесты для конфигурации логирования

## Запуск тестов

### Через скрипт

Самый простой способ запустить тесты - использовать скрипт `scripts/run_tests.sh`:

```bash
./scripts/run_tests.sh
```

### Вручную

Для запуска тестов вручную:

```bash
# Установка зависимостей для тестирования
pip install pytest pytest-cov

# Запуск всех тестов
python -m pytest

# Запуск с выводом подробной информации
python -m pytest -v

# Запуск конкретного теста
python -m pytest tests/test_telegram_alert.py

# Запуск с анализом покрытия кода
python -m pytest --cov=app tests/
```

## Добавление новых тестов

При добавлении новых функций в приложение, рекомендуется также добавлять соответствующие тесты. Для этого:

1. Создайте новый файл `test_<имя_модуля>.py` в директории `tests/`
2. Импортируйте необходимые модули и функции
3. Создайте класс с тестами, унаследованный от `unittest.TestCase`
4. Добавьте методы тестирования, начинающиеся с `test_`

Пример:

```python
import unittest
from app.main import my_new_function

class TestMyNewFunction(unittest.TestCase):
    def test_my_new_function_success(self):
        result = my_new_function(input_data)
        self.assertEqual(result, expected_output)
