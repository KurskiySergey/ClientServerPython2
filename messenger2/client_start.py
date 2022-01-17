import argparse

from PySide2.QtWidgets import QApplication
from messenger2.client.gui.welcome import WelcomeWindow

import config
from random import randint
import sys


def get_parameters(address=None, port=None, username=None, password=None):

    parser = argparse.ArgumentParser(description="client parser")
    parser.add_argument("-p", "--port", type=int, default=config.USER_PORT, help="port name")
    parser.add_argument("-a", "--address", type=str, default=config.USER_ADDRESS, help="address name")
    parser.add_argument("-u", "--username", type=str, default=f"Guest_{randint(0, 15)}", help="username")
    parser.add_argument("-k", "--key", type=str, help="password")
    args = parser.parse_args()

    if address is None:
        address_param = args.address
    else:
        address_param = address

    if port is None:
        port_param = args.port
    else:
        port_param = port

    if username is None:
        user_param = args.username
    else:
        user_param = username

    if password is None:
        password_param = args.key
    else:
        password_param = password

    return address_param, port_param, user_param, password_param


def start(ip=None, port=None, username=None, password=None):
    ip, port, username, password = get_parameters(ip, port, username, password)
    app = QApplication()
    window = WelcomeWindow(ip_address=ip, port=port, username=username, password=password)
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    start()
