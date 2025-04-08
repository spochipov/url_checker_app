
import os
import time
import logging
from logging.handlers import RotatingFileHandler
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

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

# Telegram alert
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

# Настройка HTTP-сессии с retries
def get_retry_session():
    session = requests.Session()
    retries = Retry(total=3, backoff_factor=2, status_forcelist=[500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

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

if __name__ == "__main__":
    main()
