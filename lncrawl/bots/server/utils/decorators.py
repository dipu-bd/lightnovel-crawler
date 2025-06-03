import atexit


def autoclose(func):
    def inner(*args, **kwargs):
        val = func(*args, **kwargs)
        if hasattr(val, 'close') and callable(val.close):
            atexit.register(val.close)
        return val
    return inner
