from Crypto.Cipher import PKCS1_v1_5, AES
from Crypto.Random import get_random_bytes
from Crypto.PublicKey import RSA
from messenger2.common.security.keys import get_server_public_key, get_public_key


def get_info(pk, data):
    session_key = get_random_bytes(16)
    rsa = PKCS1_v1_5.new(key=pk)
    enc_session_key = rsa.encrypt(session_key)

    aes = AES.new(session_key, AES.MODE_EAX)
    enc_text, tag = aes.encrypt_and_digest(data)
    enc_data = b"".join([enc_session_key, aes.nonce, tag, enc_text])

    return enc_data


def encript_data(username_pk, data):
    username_pk = RSA.import_key(username_pk)
    return get_info(username_pk, data)


def encript_server_data(data):
    server_pk = get_server_public_key()
    return get_info(server_pk, data)


if __name__ == "__main__":
    pass