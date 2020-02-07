import grpc
import logging
import sys
from rchain.crypto import PrivateKey
from rchain.client import RClient
import time
import subprocess

root = logging.getLogger()
root.setLevel(logging.DEBUG)

config_path = str(sys.argv[3])

with grpc.insecure_channel('localhost:40401') as channel:
    client = RClient(channel)
    with open(sys.argv[2]) as file:
        data = file.read()
        start_time = time.time()
        client.deploy_with_vabn_filled(PrivateKey.from_hex(sys.argv[1]), data, 1, 1000000000)
        dur = time.time() - start_time
        subprocess.run(['python3', 'reportInfluxDBMetric.py', 'pyrchain.deploytime', str(dur), config_path])
