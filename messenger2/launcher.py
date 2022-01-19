import subprocess
from messenger2 import config

"""
Windows launcher for starting client server messenger on local device
"""

if __name__ == "__main__":
    EVENTS = []
    while True:
        ACTION = input(
            'Для запуска сервера нажмие s, для выхода q, для запуска пользователей u\n')

        if ACTION == 's':
            server_file = f'server_start.py -p {config.SERVER_PORT}'
            process = subprocess.Popen(
                f'{config.VENV_DIR} {server_file}',
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
            EVENTS.append(process)

        if ACTION == 'u':
            users_number = int(
                input("Введите количество желаемых пользователей\n"))
            for user in range(0, users_number):
                username = f'user_{user}'
                client_file = f'client_start.py -p {config.USER_PORT} -a {config.USER_ADDRESS} -u {username} -k 1234'
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
