import os
import requests
import time
import logging
import sys

from http import HTTPStatus
from dotenv import load_dotenv
from telegram import Bot
from telegram.error import TelegramError
from exceptions import APIStatusIsNotOKError


load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Homework is checked: everithing is fine. Hooray!',
    'reviewing': 'Homework submitted for the review.',
    'rejected': 'Homework is checked: the reviewer has comments.'
}


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)
handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)


def send_message(bot, message):
    """Sending message by bot."""
    try:
        bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message
        )
        logging.info(f'Bot sent message {message}')
    except TelegramError:
        logging.error('Error while sending the message')


def get_api_answer(current_timestamp):
    """Sending a request to the endpoint of Practicum.Homework API."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    response = requests.get(ENDPOINT, headers=HEADERS, params=params)
    if response.status_code != HTTPStatus.OK:
        raise APIStatusIsNotOKError('Error while accessing the API')
    return response.json()


def check_response(response):
    """API response check for correctness."""
    if isinstance(response, dict) & (len(response) == 2):
        homeworks = response.get('homeworks')
        if isinstance(homeworks, list):
            return homeworks
    raise TypeError('Incorrect API response is received')


def parse_status(homework):
    """Getting the specific homework status."""
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    for var_name, var in {
        'homework_name': homework_name,
        'homework_status': homework_status
    }.items():
        if not var:
            message = f'{var_name} not sent'
            logging.error(message)
            raise KeyError(message)
    verdict = HOMEWORK_STATUSES.get(homework_status)
    if verdict:
        return (
            f'Check status change for homework "{homework_name}". {verdict}'
        )
    message = 'Unknown homework status'
    logging.error(message)
    raise ValueError(message)


def check_tokens():
    """Checking the availability of required environment variables."""
    required_variables = {
        'PRACTICUM_TOKEN': PRACTICUM_TOKEN,
        'TELEGRAM_TOKEN': TELEGRAM_TOKEN,
        'TELEGRAM_CHAT_ID': TELEGRAM_CHAT_ID,
    }
    for var_name, variable in required_variables.items():
        if not variable:
            logging.critical(
                f'Required environment variable is not found: {var_name}. '
                'The program is forcibly stopped.'
            )
            return False
    return True


def main():
    """The main logic of the bot."""
    if not check_tokens():
        sys.exit(
            'Required environment variable is not found. The program is '
            'forcibly stopped.'
        )
    bot = Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    while True:
        try:
            response = get_api_answer(current_timestamp)
            homeworks = check_response(response)
            if homeworks:
                message = parse_status(homeworks[0])
                send_message(bot, message)
            else:
                logging.debug('No new statuses')
            current_timestamp = response.get(
                'current_date',
                current_timestamp
            )
            time.sleep(RETRY_TIME)
        except Exception as error:
            message = f'Error while program operation: {error}'
            logging.error(message)
            send_message(bot, message)
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
