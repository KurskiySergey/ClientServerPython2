import subprocess
import config


EVENTS = []
while True:
    ACTION = input('Для запуска сервера нажмие s, для выхода q, для запуска пользователей u\n')

    if ACTION == 's':
        server_file = f'server.py -p {config.SERVER_PORT}'
        process = subprocess.Popen(
            f'{config.VENV_DIR} {server_file}',
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        EVENTS.append(process)

    if ACTION == 'u':
        users_number = int(input("Введите количество желаемых пользователей\n"))
        for user in range(0, users_number):
            username = f'user_{user}'
            client_file = f'client_start.py -p {config.USER_PORT} -a {config.USER_ADDRESS} -u {username}'
            process = subprocess.Popen(
                f'{config.VENV_DIR} {client_file}',
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
            EVENTS.append(process)

    if ACTION == 'q':
        while EVENTS:
            EVENT = EVENTS.pop()
            EVENT.kill()
        break