# -*- coding: utf-8 -*-
import os

# The special signal character for crawler commands
signal = os.getenv('DISCORD_SIGNAL_CHAR') or '!'
max_workers = os.getenv('DISCORD_MAX_WORKERS', 10)

# The public ip and path of the server to put files in
public_ip = os.getenv('PUBLIC_ADDRESS', None)
public_path = os.getenv('PUBLIC_DATA_PATH', None)
