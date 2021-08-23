import time
from json.decoder import JSONDecodeError

def loop(func):
    def wrapper(self):
        while True:
            try:
                func(self)
            except (ValueError, ConnectionError, JSONDecodeError):
                time.sleep(30)
                func(self)
    return wrapper
