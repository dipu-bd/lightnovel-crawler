import os
import platform
import sys

from .common import static_cached_property


class Screen:
    width = 1920
    height = 1080
    view_width = 1920
    view_height = 1080


class Platform:
    @static_cached_property
    @staticmethod
    def name():
        return platform.platform()

    @static_cached_property
    @staticmethod
    def system():
        return platform.system()

    @static_cached_property
    @staticmethod
    def java():
        return Platform.system == "Java"

    @static_cached_property
    @staticmethod
    def mac():
        return Platform.system == "Darwin"

    @static_cached_property
    @staticmethod
    def linux():
        return Platform.system == "Linux"

    @static_cached_property
    @staticmethod
    def cygwin():
        return sys.platform.startswith("cygwin")

    @static_cached_property
    @staticmethod
    def posix():
        return sys.platform.startswith(("darwin", "cygwin", "linux"))

    @static_cached_property
    @staticmethod
    def windows():
        return Platform.system == "Windows"

    @static_cached_property
    @staticmethod
    def wsl():
        return "wsl" in platform.release().lower()

    @static_cached_property
    @staticmethod
    def docker():
        if os.path.isfile("/.dockerenv"):
            return True
        path = "/proc/self/cgroup"
        if os.path.isfile(path):
            with open(path, encoding="utf-8") as f:
                if "docker" in f.read():
                    return True
        return False

    @static_cached_property
    @staticmethod
    def has_display():
        try:
            from tkinter import Tk
            tk = Tk()
            Screen.width = tk.winfo_screenwidth()
            Screen.height = tk.winfo_screenheight()
            Screen.view_width = tk.maxsize()[0]
            Screen.view_height = tk.maxsize()[1]
            tk.destroy()
            del tk

            return True
        except Exception:
            try:
                import matplotlib  # type:ignore
                backend = matplotlib.get_backend()
                return "Agg" not in backend
            except Exception:
                return False
