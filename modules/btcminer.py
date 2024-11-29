import socket
import json
import hashlib
import time
import threading
import pyopencl as cl
import numpy as np
import os
import sys

"""
Wanted to mine BTC by GPU but this is not good idea for Trojan
"""

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

        # Automatically set the OpenCL context to use the default device
        os.environ['PYOPENCL_CTX'] = '0'

        # Initialize OpenCL context and queue
        self.ctx = cl.create_some_context()
        self.queue = cl.CommandQueue(self.ctx)

        # Build the OpenCL program
        self.build_opencl_program()


    # Method to receive a line from the pool, handling partial messages
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


    def build_opencl_program(self):
        # OpenCL kernel code for double SHA-256 hashing
        self.kernel_code = """
        __constant uint K[64] = {
            0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5,
            0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
            0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3,
            0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
            0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc,
            0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
            0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7,
            0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
            0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13,
            0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
            0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3,
            0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
            0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5,
            0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
            0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208,
            0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2
        };

        // Helper functions for SHA-256
        static inline uint ROTR(uint x, uint n) {
            return (x >> n) | (x << (32 - n));
        }

        static inline uint SHR(uint x, uint n) {
            return x >> n;
        }

        static inline uint Ch(uint x, uint y, uint z) {
            return (x & y) ^ (~x & z);
        }

        static inline uint Maj(uint x, uint y, uint z) {
            return (x & y) ^ (x & z) ^ (y & z);
        }

        static inline uint Sigma0(uint x) {
            return ROTR(x, 2) ^ ROTR(x, 13) ^ ROTR(x, 22);
        }

        static inline uint Sigma1(uint x) {
            return ROTR(x, 6) ^ ROTR(x, 11) ^ ROTR(x, 25);
        }

        static inline uint sigma0(uint x) {
            return ROTR(x, 7) ^ ROTR(x, 18) ^ SHR(x, 3);
        }

        static inline uint sigma1(uint x) {
            return ROTR(x, 17) ^ ROTR(x, 19) ^ SHR(x, 10);
        }

        // SHA-256 transformation function
        void sha256_transform(uint *state, const uchar data[64]) {
            uint w[64];
            #pragma unroll 16
            for (int i = 0; i < 16; i++) {
                w[i] = ((uint)data[i * 4 + 0] << 24) |
                       ((uint)data[i * 4 + 1] << 16) |
                       ((uint)data[i * 4 + 2] << 8) |
                       ((uint)data[i * 4 + 3]);
            }
            #pragma unroll
            for (int i = 16; i < 64; i++) {
                w[i] = sigma1(w[i - 2]) + w[i - 7] + sigma0(w[i - 15]) + w[i - 16];
            }

            uint a = state[0];
            uint b = state[1];
            uint c = state[2];
            uint d = state[3];
            uint e = state[4];
            uint f = state[5];
            uint g = state[6];
            uint h = state[7];

            #pragma unroll
            for (int i = 0; i < 64; i++) {
                uint T1 = h + Sigma1(e) + Ch(e, f, g) + K[i] + w[i];
                uint T2 = Sigma0(a) + Maj(a, b, c);
                h = g;
                g = f;
                f = e;
                e = d + T1;
                d = c;
                c = b;
                b = a;
                a = T1 + T2;
            }

            state[0] += a;
            state[1] += b;
            state[2] += c;
            state[3] += d;
            state[4] += e;
            state[5] += f;
            state[6] += g;
            state[7] += h;
        }

        // OpenCL kernel for mining
        __kernel void sha256_kernel(
            __global const uchar *header_prefix,
            ulong nonce_start,
            __global ulong *nonce_out,
            __global uchar *hash_out,
            __global int *found,
            __global const uchar *target
        ) {
            ulong gid = get_global_id(0);
            ulong nonce = nonce_start + gid;

            uchar header[80];
            // Copy header prefix (without nonce)
            for (int i = 0; i < 76; i++) {
                header[i] = header_prefix[i];
            }

            // Set the nonce (little-endian)
            header[76] = nonce & 0xFF;
            header[77] = (nonce >> 8) & 0xFF;
            header[78] = (nonce >> 16) & 0xFF;
            header[79] = (nonce >> 24) & 0xFF;

            // First SHA-256 hash
            uint state[8] = {
                0x6a09e667,
                0xbb67ae85,
                0x3c6ef372,
                0xa54ff53a,
                0x510e527f,
                0x9b05688c,
                0x1f83d9ab,
                0x5be0cd19
            };

            sha256_transform(state, header);

            uchar hash1[32];
            for (int i = 0; i < 8; i++) {
                hash1[i * 4 + 0] = (state[i] >> 24) & 0xFF;
                hash1[i * 4 + 1] = (state[i] >> 16) & 0xFF;
                hash1[i * 4 + 2] = (state[i] >> 8) & 0xFF;
                hash1[i * 4 + 3] = state[i] & 0xFF;
            }

            // Second SHA-256 hash
            state[0] = 0x6a09e667;
            state[1] = 0xbb67ae85;
            state[2] = 0x3c6ef372;
            state[3] = 0xa54ff53a;
            state[4] = 0x510e527f;
            state[5] = 0x9b05688c;
            state[6] = 0x1f83d9ab;
            state[7] = 0x5be0cd19;

            sha256_transform(state, hash1);

            uchar hash[32];
            for (int i = 0; i < 8; i++) {
                hash[i * 4 + 0] = (state[i] >> 24) & 0xFF;
                hash[i * 4 + 1] = (state[i] >> 16) & 0xFF;
                hash[i * 4 + 2] = (state[i] >> 8) & 0xFF;
                hash[i * 4 + 3] = state[i] & 0xFF;
            }

            // Compare hash with target
            int less = 0;
            for (int i = 0; i < 32; i++) {
                uchar h = hash[31 - i];
                uchar t = target[31 - i];
                if (h < t) {
                    less = 1;
                    break;
                } else if (h > t) {
                    break;
                }
            }

            // If a valid nonce is found, store it
            if (less && atomic_cmpxchg(found, 0, 1) == 0) {
                *nonce_out = nonce;
                for (int i = 0; i < 32; i++) {
                    hash_out[i] = hash[i];
                }
            }
        }
        """
        # Build the OpenCL program
        self.program = cl.Program(self.ctx, self.kernel_code).build()


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
        # Handle authorization response if needed


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
        # self.clean_jobs = params[8]  # Some pools may not send this parameter


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
        target_hexstr = '%064x' % target
        target_bin = bytes.fromhex(target_hexstr)
        return target_bin


    # Main mining loop
    def mine(self):
        nonce_range = 0xFFFFFFFF  # Full range of 32-bit nonce
        nonce_increment = 2**20   # Nonce range per kernel execution (adjusted for testing)
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
                        print("New job received")
                    elif data.get('method') == 'mining.set_difficulty':
                        self.difficulty = data['params'][0]
                        print(f"Difficulty set to {self.difficulty}")
                    # Handle other methods if necessary
                    line = self.recv_line()  # Get the next line
            except Exception as e:
                print(f"Exception: {e}")
                continue

            # Start mining if job data is available
            if self.job_id:
                try:
                    # Calculate the target
                    target_bin = self.nbits_to_target(self.nbits)
                    assert len(target_bin) == 32, f"Target length is {len(target_bin)}, expected 32 bytes"
                    target_buf = cl.Buffer(self.ctx, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR, hostbuf=target_bin)

                    extranonce2 = self.extranonce2
                    coinbase_hash_bin = self.assemble_coinbase(extranonce2)
                    merkle_root = self.build_merkle_root(coinbase_hash_bin)
                    # merkle_root is already in bytes, reverse it
                    merkle_root_le = merkle_root[::-1]

                    # Construct the block header prefix (without nonce)
                    version_bin = bytes.fromhex(self.version)
                    version_le = version_bin[::-1]
                    prevhash_le = bytes.fromhex(self.prevhash)[::-1]
                    ntime_le = bytes.fromhex(self.ntime)[::-1]
                    nbits_le = bytes.fromhex(self.nbits)[::-1]

                    header_prefix_bin = (
                        version_le +
                        prevhash_le +
                        merkle_root_le +
                        ntime_le +
                        nbits_le
                    )

                    # Ensure header prefix is 76 bytes
                    assert len(header_prefix_bin) == 76, f"Header prefix length is {len(header_prefix_bin)}, expected 76"

                    # Prepare data for the kernel
                    header_buf = cl.Buffer(
                        self.ctx,
                        cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR,
                        hostbuf=header_prefix_bin
                    )
                    nonce_out = np.zeros(1, dtype=np.uint64)
                    nonce_out_buf = cl.Buffer(self.ctx, cl.mem_flags.WRITE_ONLY, nonce_out.nbytes)
                    hash_out = np.zeros(32, dtype=np.uint8)
                    hash_out_buf = cl.Buffer(self.ctx, cl.mem_flags.WRITE_ONLY, hash_out.nbytes)
                    found = np.zeros(1, dtype=np.int32)
                    found_buf = cl.Buffer(self.ctx, cl.mem_flags.READ_WRITE | cl.mem_flags.COPY_HOST_PTR, hostbuf=found)

                    # Loop over the nonce range
                    nonce_start = 0
                    while nonce_start < nonce_range and not self.should_stop:
                        start_time = time.time()
                        # Set up kernel arguments
                        local_size = (256,)  # Adjust based on your GPU
                        global_size = (nonce_increment // local_size[0] * local_size[0],)
                        kernel = self.program.sha256_kernel
                        kernel.set_args(
                            header_buf,
                            np.uint64(nonce_start),
                            nonce_out_buf,
                            hash_out_buf,
                            found_buf,
                            target_buf
                        )
                        # Launch the kernel
                        cl.enqueue_nd_range_kernel(self.queue, kernel, global_size, local_size)
                        self.queue.finish()
                        end_time = time.time()
                        elapsed = end_time - start_time
                        hash_rate = nonce_increment / elapsed
                        print(f"Kernel executed in {elapsed:.2f} seconds, hash rate: {hash_rate:.2f} H/s")

                        # Read results
                        cl.enqueue_copy(self.queue, nonce_out, nonce_out_buf)
                        cl.enqueue_copy(self.queue, hash_out, hash_out_buf)
                        cl.enqueue_copy(self.queue, found, found_buf)
                        self.queue.finish()

                        # Check if a valid nonce was found
                        if found[0]:
                            nonce = nonce_out[0]
                            print(f"Valid nonce found: {nonce}")
                            extranonce2_hex = '{:0{width}x}'.format(
                                extranonce2, width=self.extranonce2_size * 2)
                            self.submit_share(nonce, extranonce2_hex)
                            break  # Exit the loop after finding a valid nonce

                        else:
                            print(f"No valid nonce found in range {nonce_start} to {nonce_start + nonce_increment}")
                            # Reset 'found' flag for the next iteration
                            found[0] = 0
                            cl.enqueue_copy(self.queue, found_buf, found)

                        # Increment nonce_start
                        nonce_start += nonce_increment

                    # Increment extranonce2 for the next attempt
                    self.extranonce2 += 1
                except Exception as e:
                    print(f"Exception during mining: {e}")
                    traceback.print_exc()
            else:
                time.sleep(1)


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
        response = self.recv_line()
        data = json.loads(response)
        if data.get('result'):
            print("Share accepted")
        else:
            print("Share rejected")


if __name__ == "__main__":
    miner = Miner()
    miner.connect()
    miner.subscribe()
    miner.authorize()

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