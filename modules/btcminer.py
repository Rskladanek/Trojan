import socket
import json
import hashlib
import threading
import time
import sys


# Pool address and port
POOL_ADDRESS = "btc-euro.f2pool.com"
POOL_PORT = 1315  # Ensure this is the correct port for the pool


# Wallet address and worker name
USERNAME = "wageta.001"
PASSWORD = "21235365876986800"


# Double SHA-256 hashing function
def double_sha256(data):
    return hashlib.sha256(hashlib.sha256(data).digest()).digest()


# Miner class to manage mining operations
class Miner:
    def __init__(self):
        # Initialize network variables
        self.sock = None
        self.subscription_id = None
        self.extranonce1 = None
        self.extranonce2_size = None
        self.recv_buffer = ''
        # Initialize mining variables
        self.difficulty = 1
        self.job_id = None
        self.prevhash = None
        self.coinb1 = None
        self.coinb2 = None
        self.merkle_branch = []
        self.version = None
        self.nbits = None
        self.ntime = None
        self.extranonce2 = 0
        self.should_stop = False


    # Method to receive a line from the pool
    def recv_line(self):
        while True:
            if '\n' in self.recv_buffer:
                line, self.recv_buffer = self.recv_buffer.split('\n', 1)
                return line
            try:
                data = self.sock.recv(1024).decode('utf-8')
                if not data:
                    return ''
                self.recv_buffer += data
            except socket.timeout:
                continue
            except Exception as e:
                print(f"Socket error: {e}")
                return ''


    # Connect to the mining pool
    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((POOL_ADDRESS, POOL_PORT))
        self.sock.settimeout(5)


    # Send data to the pool
    def send(self, data):
        message = json.dumps(data).encode('utf-8') + b'\n'
        self.sock.sendall(message)


    # Authorize with the mining pool
    def authorize(self):
        auth_payload = {
            "id": 2,
            "method": "mining.authorize",
            "params": [USERNAME, PASSWORD]
        }
        self.send(auth_payload)
        response = self.recv_line()
        print(f"Authorize response: {response}")


    # Subscribe to the mining pool
    def subscribe(self):
        subscribe_payload = {
            "id": 1,
            "method": "mining.subscribe",
            "params": []
        }
        self.send(subscribe_payload)
        response = self.recv_line()
        data = json.loads(response)
        if data['result']:
            self.subscription_id = data['result'][0]
            self.extranonce1 = data['result'][1]
            self.extranonce2_size = data['result'][2]
            print(f"Subscribed successfully: Extranonce1={self.extranonce1}, Extranonce2_size={self.extranonce2_size}")
        else:
            raise Exception("Failed to subscribe")


    # Set new mining job
    def set_job(self, params):
        self.job_id = params[0]
        self.prevhash = params[1]
        self.coinb1 = params[2]
        self.coinb2 = params[3]
        self.merkle_branch = params[4]
        self.version = params[5]
        self.nbits = params[6]
        self.ntime = params[7]
        print(f"New job received: Job ID={self.job_id}")


    # Assemble the coinbase transaction
    def assemble_coinbase(self, extranonce2):
        extranonce2_hex = '{:0{width}x}'.format(extranonce2, width=self.extranonce2_size * 2)
        coinbase_hex = self.coinb1 + self.extranonce1 + extranonce2_hex + self.coinb2
        coinbase_bin = bytes.fromhex(coinbase_hex)
        coinbase_hash_bin = double_sha256(coinbase_bin)
        return coinbase_hash_bin


    # Build the Merkle root
    def build_merkle_root(self, coinbase_hash_bin):
        merkle_root = coinbase_hash_bin
        for branch in self.merkle_branch:
            branch_bin = bytes.fromhex(branch)
            merkle_root = double_sha256(merkle_root + branch_bin)
        return merkle_root


    # Convert nBits to target
    def nbits_to_target(self, nbits):
        nbits_int = int(nbits, 16)
        exponent = nbits_int >> 24
        mantissa = nbits_int & 0xFFFFFF
        target = mantissa * (1 << (8 * (exponent - 3)))
        return target


    # Main mining loop
    def mine(self):
        nonce_range = 0xFFFFFFFF
        while not self.should_stop:
            # Receive data from the pool
            try:
                line = self.recv_line()
                while line:
                    print(f"Received line: {line}")
                    try:
                        data = json.loads(line)
                    except json.JSONDecodeError as e:
                        print(f"JSON decoding error: {e}")
                        break  # Exit the loop and continue receiving
                    if data.get('method') == 'mining.notify':
                        self.set_job(data['params'])
                    elif data.get('method') == 'mining.set_difficulty':
                        self.difficulty = data['params'][0]
                        print(f"Difficulty set to {self.difficulty}")
                    elif data.get('result') == True and data.get('id') == 4:
                        print("Share accepted")
                    elif data.get('result') == False and data.get('id') == 4:
                        print("Share rejected")
                    # Handle other methods if necessary
                    line = self.recv_line()  # Get the next line
            except Exception as e:
                print(f"Exception: {e}")
                continue

            if not self.job_id:
                time.sleep(1)
                continue

            extranonce2 = self.extranonce2
            coinbase_hash_bin = self.assemble_coinbase(extranonce2)
            merkle_root = self.build_merkle_root(coinbase_hash_bin)
            merkle_root_le = merkle_root[::-1]

            version_le = bytes.fromhex(self.version)[::-1]
            prevhash_le = bytes.fromhex(self.prevhash)[::-1]
            ntime_le = bytes.fromhex(self.ntime)[::-1]
            nbits_le = bytes.fromhex(self.nbits)[::-1]

            header_prefix = version_le + prevhash_le + merkle_root_le + ntime_le + nbits_le
            target_int = self.nbits_to_target(self.nbits)

            # Prepare target as an integer for comparison
            max_target = 0xFFFF * 2 ** (8 * (0x1d - 3))
            target = max_target // self.difficulty

            start_time = time.time()
            for nonce in range(0xFFFFFFFF):
                if self.should_stop:
                    break

                nonce_bytes = nonce.to_bytes(4, byteorder='little')
                header = header_prefix + nonce_bytes
                hash_result = double_sha256(header)
                hash_int = int.from_bytes(hash_result, byteorder='big')

                if hash_int < target:
                    print(f"Valid nonce found: {nonce}")
                    extranonce2_hex = '{:0{width}x}'.format(
                        extranonce2, width=self.extranonce2_size * 2)
                    self.submit_share(nonce, extranonce2_hex)
                    break

            elapsed_time = time.time() - start_time
            print(f"Mining loop took {elapsed_time:.2f} seconds")
            self.extranonce2 += 1


    # Submit a valid share to the pool
    def submit_share(self, nonce, extranonce2_hex):
        submit_payload = {
            "id": 4,
            "method": "mining.submit",
            "params": [
                USERNAME,
                self.job_id,
                extranonce2_hex,
                self.ntime,
                '{:08x}'.format(nonce)
            ]
        }
        self.send(submit_payload)
        print(f"Share submitted: nonce={nonce}, extranonce2={extranonce2_hex}")


    # Start listening to the server in a separate thread
    def listen(self):
        while not self.should_stop:
            try:
                line = self.recv_line()
                if line:
                    print(f"Server message: {line}")
                    data = json.loads(line)
                    if data.get('method') == 'mining.notify':
                        self.set_job(data['params'])
                    elif data.get('method') == 'mining.set_difficulty':
                        self.difficulty = data['params'][0]
                        print(f"Difficulty set to {self.difficulty}")
                    elif data.get('id') == 4:
                        if data.get('result'):
                            print("Share accepted")
                        else:
                            print("Share rejected")
                else:
                    time.sleep(0.1)
            except Exception as e:
                print(f"Listening error: {e}")
                time.sleep(1)


def run(**args):
    miner = Miner()
    miner.connect()
    miner.subscribe()
    miner.authorize()

    # Start listening to the server
    listener_thread = threading.Thread(target=miner.listen)
    listener_thread.daemon = True
    listener_thread.start()

    # Start mining
    mining_thread = threading.Thread(target=miner.mine)

    try:
        mining_thread.start()
    except KeyboardInterrupt:
        print("Interrupted during mining_thread.start()")
        sys.exit()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping miner")
        miner.should_stop = True
        mining_thread.join()
