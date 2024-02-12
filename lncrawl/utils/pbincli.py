"""
Source: https://github.com/r4sas/PBinCLI/blob/master/pbincli/format.py
"""
import json
import logging
import ntpath
import os
import zlib
from base64 import b64decode, b64encode
from hashlib import sha256
from json import loads as json_decode
from mimetypes import guess_type

from base58 import b58decode, b58encode

# -----------------------------------------------------------------------------#

logger = logging.getLogger(__name__)


class PBinCLIException(Exception):
    pass


def PBinCLIError(message):
    logger.warning("PBinCLI Error: {}".format(message))


def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)


def check_readable(f):
    # Checks if path exists and readable
    if not os.path.exists(f) or not os.access(f, os.R_OK):
        PBinCLIError("Error accessing path: {}".format(f))


def check_writable(f):
    # Checks if path is writable
    if not os.access(os.path.dirname(f) or ".", os.W_OK):
        PBinCLIError("Path is not writable: {}".format(f))


def json_encode(s):
    return json.dumps(s, separators=(",", ":")).encode()


def validate_url(s):
    if not s.endswith("/"):
        s = s + "/"
    return s


# -----------------------------------------------------------------------------#


# try import AES cipher and check if it has GCM mode (prevent usage of pycrypto)
try:
    from Crypto.Cipher import AES
    from Crypto.Random import get_random_bytes
except ImportError:
    PBinCLIError(
        "pycryptodome not found.\n" "    pip install pycryptodome>=3.0.0,<4.0.0"
    )


CIPHER_ITERATION_COUNT = 100000
CIPHER_SALT_BYTES = 8
CIPHER_BLOCK_BITS = 256
CIPHER_TAG_BITS = 128


class PasteV2:
    def __init__(self, debug=False):
        self._compression = "zlib"
        self._data = ""
        self._text = ""
        self._attachment = ""
        self._attachment_name = ""
        self._password = ""
        self._debug = debug
        self._iteration_count = CIPHER_ITERATION_COUNT
        self._salt_bytes = CIPHER_SALT_BYTES
        self._block_bits = CIPHER_BLOCK_BITS
        self._tag_bits = CIPHER_TAG_BITS
        self._key = get_random_bytes(int(self._block_bits / 8))

    def setPassword(self, password):
        self._password = password

    def setText(self, text):
        self._text = text

    def setAttachment(self, path):
        check_readable(path)
        with open(path, "rb") as f:
            contents = f.read()
            f.close()
        mime = guess_type(path, strict=False)[0]

        # MIME fallback
        if not mime:
            mime = "application/octet-stream"

        if self._debug:
            logger.debug("Filename:\t{}\nMIME-type:\t{}".format(path_leaf(path), mime))

        self._attachment = "data:" + mime + ";base64," + b64encode(contents).decode()
        self._attachment_name = path_leaf(path)

    def setCompression(self, comp):
        self._compression = comp

    def getText(self):
        return self._text

    def getAttachment(self):
        return (
            [b64decode(self._attachment.split(",", 1)[1]), self._attachment_name]
            if self._attachment
            else [False, False]
        )

    def getJSON(self):
        return json_encode(self._data).decode()

    def loadJSON(self, data):
        self._data = data

    def getHash(self):
        return b58encode(self._key).decode()

    def setHash(self, passphrase):
        self._key = b58decode(passphrase)

    def __deriveKey(self, salt):
        from Crypto.Hash import HMAC, SHA256
        from Crypto.Protocol.KDF import PBKDF2

        # Key derivation, using PBKDF2 and SHA256 HMAC
        return PBKDF2(
            self._key + self._password.encode(),
            salt,
            dkLen=int(self._block_bits / 8),
            count=self._iteration_count,
            prf=lambda password, salt: HMAC.new(password, salt, SHA256).digest(),
        )

    @classmethod
    def __initializeCipher(cls, key, iv, adata, tagsize):
        cipher = AES.new(key, AES.MODE_GCM, nonce=iv, mac_len=tagsize)
        cipher.update(json_encode(adata))
        return cipher

    def __preparePassKey(self):
        if self._password:
            digest = sha256(self._password.encode("UTF-8")).hexdigest()
            return b64encode(self._key) + digest.encode("UTF-8")
        else:
            return b64encode(self._key)

    def __decompress(self, s):
        if self._compression == "zlib":
            # decompress data
            return zlib.decompress(s, -zlib.MAX_WBITS)
        elif self._compression == "none":
            # nothing to do, just return original data
            return s
        else:
            PBinCLIError("Unknown compression type provided in paste!")

    def __compress(self, s):
        if self._compression == "zlib":
            # using compressobj as compress doesn't let us specify wbits
            # needed to get the raw stream without headers
            co = zlib.compressobj(wbits=-zlib.MAX_WBITS)
            return co.compress(s) + co.flush()
        elif self._compression == "none":
            # nothing to do, just return original data
            return s
        else:
            PBinCLIError("Unknown compression type provided!")

    def decrypt(self):
        # that is wrapper which running needed function regrading to paste version
        iv = b64decode(self._data["adata"][0][0])
        salt = b64decode(self._data["adata"][0][1])

        self._iteration_count = self._data["adata"][0][2]
        self._block_bits = self._data["adata"][0][3]
        self._tag_bits = self._data["adata"][0][4]
        cipher_tag_bytes = int(self._tag_bits / 8)

        key = self.__deriveKey(salt)

        # Get compression type from received paste
        self._compression = self._data["adata"][0][7]

        cipher = self.__initializeCipher(key, iv, self._data["adata"], cipher_tag_bytes)
        # Cut the cipher text into message and tag
        cipher_text_tag = b64decode(self._data["ct"])
        cipher_text = cipher_text_tag[:-cipher_tag_bytes]
        cipher_tag = cipher_text_tag[-cipher_tag_bytes:]
        cipher_message = json_decode(
            self.__decompress(
                cipher.decrypt_and_verify(cipher_text, cipher_tag)
            ).decode()
        )

        self._text = cipher_message["paste"].encode()

        if "attachment" in cipher_message and "attachment_name" in cipher_message:
            self._attachment = cipher_message["attachment"]
            self._attachment_name = cipher_message["attachment_name"]
