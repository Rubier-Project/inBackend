import base64
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad, unpad

class inCrypto(object):
    def __init__(self) -> None:
        self.iv = bytes.fromhex("0"*32)

    def encrypt(self, string: str, key: str):
        try:
            cipher = AES.new(key.encode(), AES.MODE_CBC, self.iv)
            data_pad = pad(string.encode(), AES.block_size)
            return {"enc": base64.b64encode(cipher.encrypt(data_pad)).decode(), "error": False}
        except Exception as er:
            return {"enc": str(er), "error": True}

    def decrypt(self, string: str, key: str):
        try:
            decipher = AES.new(key.encode(), AES.MODE_CBC, self.iv)
            decoded_data = base64.b64decode(string)
            data_unpad = unpad(decipher.decrypt(decoded_data), AES.block_size)
            return {"dec": data_unpad.decode(), "error": False}
        except Exception as er:
            return {"dec": str(er), "error": True}


class CryptoServer:
    def __init__(self, key: int) -> None:
        self.key = key
        self.keyReal = 1
        if self.key != self.keyReal:
            raise ValueError('Invalid key')

    def encrypt(self, data):
        encrypted = ''.join(chr((ord(char) + self.key) % 256) for char in data)
        return encrypted

    def decrypt(self, data):
        decrypted = ''.join(chr((ord(char) - self.key) % 256) for char in data)
        return decrypted