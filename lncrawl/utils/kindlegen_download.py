import os
import platform
import tarfile
import tempfile
from io import BytesIO, FileIO
from logging import Logger
from zipfile import ZipFile

import requests

from ..core.exeptions import LNException

logger = Logger("KINDLEGEN")

WINDOWS_URL = "http://kindlegen.s3.amazonaws.com/kindlegen_win32_v2_9.zip"
MACOS_URL = "http://kindlegen.s3.amazonaws.com/KindleGen_Mac_i386_v2_9.zip"
LINUX_URL = "http://kindlegen.s3.amazonaws.com/kindlegen_linux_2.6_i386_v2_9.tar.gz"


def get_url_by_platform():
    if platform.system() == "Linux":
        return LINUX_URL
    elif platform.system() == "Darwin":
        return MACOS_URL
    elif platform.system() == "Windows":
        return WINDOWS_URL
    else:
        raise LNException("Unrecognized platform")


def extract_kindlegen_file(extractor, file_list):
    logger.debug(file_list)
    home = os.path.expanduser("~")
    if file_list.count("kindlegen") == 1:
        extractor("kindlegen", path=home)
        logger.info("Extracted kindlegen to %s", home)
    elif file_list.count("kindlegen.exe") == 1:
        extractor("kindlegen.exe", path=home)
        logger.info("Extracted kindlegen.exe to %s", home)
        os.rename(os.path.join(home, "kindlegen.exe"), os.path.join(home, "kindlegen"))
        logger.info("Renamed kindlegen.exe to kindlegen")
    else:
        raise LNException("Kindlegen executable was not found.")


def download_kindlegen():
    # Download the file
    url = get_url_by_platform()
    print("Downloading kindlegen...")
    byte_array = requests.get(url).content

    # Extract contents
    print("Extracting kindlegen...")
    if url.endswith(".zip"):
        with BytesIO(byte_array) as byte_stream:
            with ZipFile(byte_stream) as file:
                extract_kindlegen_file(file.extract, file.namelist())

    elif url.endswith(".tar.gz"):
        temp_file = tempfile.mktemp(".tar.gz")
        try:
            logger.info("Writing content to %s", temp_file)
            with FileIO(temp_file, "w") as file:
                file.write(byte_array)

            logger.info("Opening %s as archive", temp_file)
            with tarfile.open(temp_file) as file:
                extract_kindlegen_file(file.extract, file.getnames())

        finally:
            os.remove(temp_file)
            logger.info("%s removed.", temp_file)


def retrieve_kindlegen():
    # Check kindlegen availability
    home = os.path.expanduser("~")
    kindlegen_file = os.path.join(home, "kindlegen")
    if os.path.exists(kindlegen_file):
        return kindlegen_file

    return None
