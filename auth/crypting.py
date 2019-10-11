import base64
import json

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

key = get_random_bytes(16)
cipher = AES.new(key, AES.MODE_EAX)
nonce = cipher.nonce


def aes_encrypt(data: str) -> str:
    """
    Encrypt data with AES crypto algorithm.

    :param data: string to encrypt with AES
    :return: encrypted string
    """
    cipher_new = AES.new(key, AES.MODE_EAX, nonce=nonce)
    ciphertext = cipher_new.encrypt(data.encode('utf-8'))
    ciphertext = base64.b64encode(ciphertext)
    return ciphertext.decode('utf-8')


def aes_decrypt(ciphertext: str) -> str:
    cipher_new = AES.new(key, AES.MODE_EAX, nonce=nonce)
    ciphertext = ciphertext.encode()
    ciphertext = base64.b64decode(ciphertext)
    ciphertext = cipher_new.decrypt(ciphertext)
    return ciphertext.decode()


