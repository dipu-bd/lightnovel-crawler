import platform


class Platform:
    java = platform.system() == "Java"
    mac = platform.system() == "Darwin"
    linux = platform.system() == "Linux"
    windows = platform.system() == "Windows"
    wsl = "wsl" in platform.release().lower()
    name = platform.platform()
