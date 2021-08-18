import time

def loop(func):
    def wrapper(self):
        while True:
            try:
                func(self)
            except (ValueError, ConnectionError):
                time.sleep(20)
                func(self)
    return wrapper
