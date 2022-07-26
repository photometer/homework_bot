# Homework Bot
Bot for checking the status of homework for code review in Yandex.Practicum

This bot uses Yandex.Practicum API data. Works both on PC and Heroku, just
run the bot with valid tokens.
Every 10 minutes bot checks the Yandex.Practicum API and sends the status to
telegram account.
If the work is reviewed you will receive a message about the status (if there
are changes) of your code review.

The Practicum.Homework API has only [one endpoint](https://practicum.yandex.ru/api/user_api/homework_statuses/)
and access to it possible only by token.

You can get the token [here](https://oauth.yandex.ru/authorize?response_type=token&client_id=1d0b9dd4d652455a9eb710d450ff456a).
Copy it. Later it will come in handy.

### How this API works
When reviewer checks your homework, its status changes:

- homework submitted for review
- homework returned for bug fixes
- homework is accepted

If the program detects a status change during the next check (once per 10
minutes), the updated status is sent by the bot to the specified chat.

### Launch on PC

- You can clone this project:
    ```git clone https://github.com/photometer/homework_bot```

- In this project folder create and activate virtual environment
(recommendations for Windows):

    ```
    python -m venv venv
    . venv/scripts/activate
    ```

- In venv install all necessary requirements:

    ```bash
    pip install -r requirements.txt
    ```

- Import tokens for Yandex.Practicum and Telegram in console:

    ```bash
    export PRACTICUM_TOKEN=<PRACTICUM_TOKEN>
    export TELEGRAM_TOKEN=<TELEGRAM_TOKEN>
    export CHAT_ID=<CHAT_ID>
    ```
    > *NOTE:* ```TELEGRAM_TOKEN``` is the token given you by
    [@BotFather](https://t.me/botfather), ```CHAT_ID``` is the id of chat
    recipient of the status (can be obtained from
    [@userinfobot](https://t.me/userinfobot))

- Start the program:

  ```bash
  python homework.py
  ```

Автор: [Elizaveta Androsova](https://github.com/themasterid) :boom:
