import os
import configparser
from PySide2.QtCore import QCoreApplication

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

QT_PLUGINS_PATH = os.path.join(BASE_DIR, "venv\\Lib\\site-packages\\PySide2\\plugins")
QCoreApplication.setLibraryPaths([QT_PLUGINS_PATH])

config = configparser.ConfigParser()
SERVER_INI = f"{BASE_DIR}\\server.ini"
config.read(SERVER_INI)
SETTINGS = config["SETTINGS"]

SERVER_PORT = SETTINGS.get("server_port")
LISTEN_ADDRESS = SETTINGS.get("listen_address")

DATABASE_PATH = SETTINGS.get("database_path")
DATABASE_NAME = SETTINGS.get("database_file")

USER_ADDRESS = "127.0.0.1"
USER_PORT = 7777

MAX_POCKET_SIZE = 1024
MAX_CONNECTIONS = 5


LOG_DIR = os.path.join(BASE_DIR, 'messenger2\\logs')
DATABASE_DIR = os.path.join(BASE_DIR, "messenger2\\databases")
CLIENT_UI_DIR = "client\\gui\\ui"
DATABASE_ENGINE = f'sqlite:///{DATABASE_PATH}\\{DATABASE_NAME}'
CLIENT_DATABASE_ENGINE = 'sqlite:///client\\client_base_'
TEST_DATABASE_ENGINE = 'sqlite:///test_server_base.db3'
VENV_DIR = os.path.join(BASE_DIR, "venv\\Scripts\\python.exe")

CLIENT_LOG_DIR = os.path.join(LOG_DIR, 'client_logs')
SERVER_LOG_DIR = os.path.join(LOG_DIR, 'server_logs')