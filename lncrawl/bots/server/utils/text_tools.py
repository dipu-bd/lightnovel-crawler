import base64
import hashlib
import lzma

from cryptography.fernet import Fernet

__key_cache = {}


def text_compress(plain: bytes) -> bytes:
    lzc = lzma.LZMACompressor()
    output = lzc.compress(plain)
    output += lzc.flush()
    return output


def text_decompress(compressed: bytes) -> bytes:
    lzd = lzma.LZMADecompressor()
    return lzd.decompress(compressed)


def text_encrypt(plain: bytes, secret: str | bytes) -> bytes:
    fernet = Fernet(generate_key(secret))
    result = fernet.encrypt(plain)
    return base64.urlsafe_b64decode(result)


def text_decrypt(cipher: bytes, secret: str | bytes) -> bytes:
    fernet = Fernet(generate_key(secret))
    cipher = base64.urlsafe_b64encode(cipher)
    return fernet.decrypt(cipher)


def text_compress_encrypt(plain: bytes, secret: str | bytes) -> bytes:
    return text_encrypt(text_compress(plain), secret)


def text_decrypt_decompress(cipher: bytes, secret: str | bytes) -> bytes:
    return text_decompress(text_decrypt(cipher, secret))


def generate_md5(*texts) -> str:
    md5 = hashlib.md5()
    for text in texts:
        md5.update(str(text or '').encode())
    return md5.hexdigest()


def generate_key(secret: str | bytes) -> bytes:
    if isinstance(secret, str):
        secret = secret.encode()
    if secret not in __key_cache:
        hash = hashlib.sha3_256(secret).digest()
        key = base64.urlsafe_b64encode(hash)
        __key_cache[secret] = key
    return __key_cache[secret]
