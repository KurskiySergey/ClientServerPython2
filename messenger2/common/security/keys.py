from Crypto.PublicKey import RSA
import os
from messenger2.protocols.JIM import JIM
import config

SERVER_KEYS_DIR = os.path.join(config.SERVER_DIR, "server_keys")
CLIENT_KEYS_DIR = os.path.join(config.CLIENT_DIR, "client_keys")


def generate_pair(username, is_client=True):
    dir = CLIENT_KEYS_DIR
    if not is_client:
        dir = SERVER_KEYS_DIR
        username = "server"
    try:
        files = os.listdir(dir)
    except FileNotFoundError:
        os.mkdir(dir)
        files = os.listdir(dir)
    if f"public_{username}.pem" and f"private_{username}.pem" in files:
        print("keys are already exists")
    else:
        key = RSA.generate(2048)
        with open(os.path.join(dir, f"private_{username}.pem"), "wb") as f:
            f.write(key.export_key())

        with open(os.path.join(dir, f"public_{username}.pem"), "wb") as f:
            f.write(key.public_key().export_key())


def get_public_key(username, to_str=False):
    try:
        key = RSA.import_key(open(os.path.join(CLIENT_KEYS_DIR, f"public_{username}.pem")).read())
        if to_str:
            key = str(key.public_key().export_key(), encoding=JIM.ENCODING)
        return key
    except (FileNotFoundError, FileExistsError):
        return None


def get_private_key(username, to_str=False):
    try:
        key = RSA.import_key(open(os.path.join(CLIENT_KEYS_DIR, f"private_{username}.pem")).read())
        if to_str:
            key = str(key.public_key().export_key(), encoding=JIM.ENCODING)
        return key
    except (FileNotFoundError, FileExistsError):
        return None


def get_server_public_key(to_str=False):
    try:
        with open(os.path.join(SERVER_KEYS_DIR, "public_server.pem"), "rb") as server_key:
            key = RSA.import_key(server_key.read())
            if to_str:
                key = str(key.public_key().export_key(), encoding=JIM.ENCODING)
            return key
    except (FileNotFoundError, FileExistsError):
        return None


def get_client_server_public_key(to_str=False):
    try:
        with open(os.path.join(CLIENT_KEYS_DIR, "public_server.pem"), "rb") as server_key:
            key = RSA.import_key(server_key.read())
            if to_str:
                key = str(key.public_key().export_key(), encoding=JIM.ENCODING)
            return key
    except (FileNotFoundError, FileExistsError):
        return None


def get_server_private_key(to_str=False):
    try:
        with open(os.path.join(SERVER_KEYS_DIR, "private_server.pem"), "rb") as server_key:
            key = RSA.import_key(server_key.read())
            if to_str:
                key = str(key.export_key(), encoding=JIM.ENCODING)
            return key
    except (FileNotFoundError, FileExistsError):
        return None


def save_server_public_key(server_pk):
    with open(os.path.join(CLIENT_KEYS_DIR, "public_server.pem"), "wb") as server_key:
        server_key.write(bytes(server_pk, encoding=JIM.ENCODING))


if __name__ == "__main__":
    generate_pair("server")