import argparse

from PySide2.QtWidgets import QApplication
from messenger2.databases.database import ClientDatabase
from messenger2.client.transport import ClientTransport
from messenger2.client.gui.client_window import ClientWindow
import sys
import os

import config
from random import randint


def get_parameters(address=None, port=None, username=None):

    parser = argparse.ArgumentParser(description="client parser")
    parser.add_argument("-p", "--port", type=int, default=config.USER_PORT, help="port name")
    parser.add_argument("-a", "--address", type=str, default=config.USER_ADDRESS, help="address name")
    parser.add_argument("-u", "--username", type=str, default=f"Guest_{randint(0, 15)}", help="username")
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

    return address_param, port_param, user_param


def start(ip=None, port=None, username=None):
    ip, port, username = get_parameters(ip, port, username)
    app = QApplication()
    engine = f"{config.CLIENT_DATABASE_ENGINE}{username}.db3"
    database = ClientDatabase(engine=engine)
    transport = ClientTransport(ip_address=ip, port=port, database=database,
                                username=username)
    transport.setDaemon(True)
    transport.start()
    window = ClientWindow(database=database, transport=transport, username=username, ui_file=os.path.join(config.CLIENT_UI_DIR, "client.ui"))
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    start()
