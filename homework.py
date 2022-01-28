import os
import requests
import time
import logging

from dotenv import load_dotenv
from telegram import Bot
from exceptions import APIStatusIsNotOKError


load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
logger.addHandler(handler)


def send_message(bot, message):
    """Отправка сообщения ботом."""
    try:
        bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message
        )
        logging.info(f'Бот отправил сообщение {message}')
    except Exception:
        logging.error('Сбой при отправке сообщения')


def get_api_answer(current_timestamp):
    """Отправка запроса к эндпоинту API сервиса Практикум.Домашка."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    response = requests.get(ENDPOINT, headers=HEADERS, params=params)
    if response.status_code != 200:
        raise APIStatusIsNotOKError('Возникла ошибка при обращении к API')
    return response.json()


def check_response(response):
    """Проверка ответа API на корректность."""
    if isinstance(response, dict) & (len(response) == 2):
        homeworks = response.get('homeworks')
        if isinstance(homeworks, list):
            return homeworks
    raise TypeError('Получен некорректный ответ API')


def parse_status(homework):
    """Извлечение статуса конкретной домашней работы."""
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    verdict = HOMEWORK_STATUSES[homework_status]
    if verdict:
        return (
            f'Изменился статус проверки работы "{homework_name}". {verdict}'
        )
    logging.error('Недокументированный статус домашней работы')


def check_tokens():
    """Проверка доступности необходимых переменных окружения."""
    required_variables = {
        'PRACTICUM_TOKEN': PRACTICUM_TOKEN,
        'TELEGRAM_TOKEN': TELEGRAM_TOKEN,
        'TELEGRAM_CHAT_ID': TELEGRAM_CHAT_ID,
    }
    for var_name, variable in required_variables.items():
        if not variable:
            logging.critical(
                f'Отсутствует обязательная переменная окружения: {var_name}. '
                'Программа принудительно остановлена.'
            )
            return False
    return True


def main():
    """Основная логика работы бота."""
    bot = Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    while True:
        try:
            response = get_api_answer(current_timestamp)
            homeworks = check_response(response)
            if 'homeworks' in homeworks:
                message = parse_status(homeworks)
                send_message(bot, message)
            else:
                logging.debug('Новых статусов не обнаружено')
            current_timestamp = int(time.time())
            time.sleep(RETRY_TIME)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logging.error(message)
            send_message(bot, message)
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
