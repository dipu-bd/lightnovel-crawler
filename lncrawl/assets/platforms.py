import os
import platform


def is_docker():
    if os.path.isfile("/.dockerenv"):
        return True
    path = "/proc/self/cgroup"
    if os.path.isfile(path):
        with open(path, encoding="utf-8") as f:
            if "docker" in f.read():
                return True
    return False


class Platform:
    name = platform.platform()
    docker = is_docker()
    java = platform.system() == "Java"
    mac = platform.system() == "Darwin"
    linux = platform.system() == "Linux"
    windows = platform.system() == "Windows"
    wsl = "wsl" in platform.release().lower()
