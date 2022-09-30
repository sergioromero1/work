import time
from json.decoder import JSONDecodeError

def loop(func):
    def wrapper(self):
        while True:
            try:
                func(self)
            except JSONDecodeError as e: #(ValueError, ConnectionError,
                print(e, flush = True)
                time.sleep(180)
    return wrapper
