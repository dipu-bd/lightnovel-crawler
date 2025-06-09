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
        return 7 * 24 * 60

    @cached_property
    def admin_email(self) -> str:
        return env('SERVER_ADMIN_EMAIL')

    @cached_property
    def admin_password(self) -> str:
        return env('SERVER_ADMIN_PASSWORD')

    @cached_property
    def database_url(self) -> str:
        return env('DATABASE_URL', 'sqlite:///sqlite.db')

    @cached_property
    def base_url(self) -> str:
        return env('SERVER_BASE_URL').strip('/')


class App:
    @property
    def output_path(self) -> str:
        return C.DEFAULT_OUTPUT_PATH

    @cached_property
    def runner_cooldown(self) -> int:
        '''time (seconds) to sleep before starting next job'''
        return int(env('RUNNER_COOLDOWN_IN_SECONDS', 5))


class Mail:
    @cached_property
    def smtp_server(self) -> str:
        return env('SMTP_SERVER', 'localhost')

    @cached_property
    def smtp_port(self) -> int:
        return int(env('SMTP_PORT', '1025'))

    @cached_property
    def smtp_username(self) -> str:
        return env('SMTP_USERNAME', '')

    @cached_property
    def smtp_password(self) -> str:
        return env('SMTP_PASSWORD', '')

    @cached_property
    def smtp_sender(self) -> str:
        return env('SMTP_SENDER', 'lncrawl@pm.me')


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

    @cached_property
    def mail(self):
        return Mail()
