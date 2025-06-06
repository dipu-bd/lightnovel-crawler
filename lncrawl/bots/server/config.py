import logging
import os
from functools import cached_property

import dotenv

from lncrawl import constants as C


def env(key, default_value=None):
    value = os.getenv(key, default_value)
    if value is None:
        raise Exception(f'Missing required ENV: {key}')
    return value


class CloudDrive:
    @cached_property
    def id(self) -> str:
        return env('CLOUD_DRIVE', 'ANONFILES')

    @cached_property
    def gdrive_credential_file(self) -> str:
        return env('GOOGLE_DRIVE_CREDENTIAL_FILE', '')

    @cached_property
    def gdrive_folder_id(self) -> str:
        return env('GOOGLE_DRIVE_FOLDER_ID', '')


class ServerConfig:
    @cached_property
    def token_secret(self) -> str:
        return env('SERVER_SECRET')

    @property
    def token_algo(self) -> str:
        return "HS256"

    @property
    def token_expiry(self) -> int:
        '''in minutes'''
        return 30

    @cached_property
    def admin_email(self) -> str:
        return env('SERVER_ADMIN_EMAIL')

    @cached_property
    def admin_password(self) -> str:
        return env('SERVER_ADMIN_PASSWORD')

    @cached_property
    def database_url(self) -> str:
        return env('DATABASE_URL', 'sqlite:///sqlite.db')


class App:
    @cached_property
    def output_path(self) -> str:
        return env('OUTPUT_PATH', C.DEFAULT_OUTPUT_PATH)

    @cached_property
    def runner_cooldown(self) -> int:
        '''time (seconds) to sleep before starting next job'''
        return int(env('RUNNER_COOLDOWN_IN_SECONDS', 5))


class Config:
    def __init__(self) -> None:
        dotenv.load_dotenv()
        logging.basicConfig(level=logging.INFO)

    @cached_property
    def server(self):
        return ServerConfig()

    @cached_property
    def cloud(self):
        return CloudDrive()

    @cached_property
    def app(self):
        return App()
