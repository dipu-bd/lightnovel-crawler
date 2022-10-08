import os
import platform
import sys


def is_docker():
    if os.path.isfile("/.dockerenv"):
        return True
    path = "/proc/self/cgroup"
    if os.path.isfile(path):
        with open(path, encoding="utf-8") as f:
            if "docker" in f.read():
                return True
    return False


class Screen:
    width = 1920
    height = 1080
    view_width = 1920
    view_height = 1080


def has_display():
    try:
        from tkinter import Tk

        tk = Tk()
        Screen.width = tk.winfo_screenwidth()
        Screen.height = tk.winfo_screenheight()
        Screen.view_width = tk.maxsize()[0]
        Screen.view_height = tk.maxsize()[1]
        tk.destroy()
        del Tk
        return True
    except Exception:
        return False


class Platform:
    name = platform.platform()
    docker = is_docker()
    display = has_display()
    java = platform.system() == "Java"
    mac = platform.system() == "Darwin"
    linux = platform.system() == "Linux"
    cygwin = sys.platform.startswith("cygwin")
    posix = sys.platform.startswith(("darwin", "cygwin", "linux"))
    windows = platform.system() == "Windows"
    wsl = "wsl" in platform.release().lower()
