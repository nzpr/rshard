import grpc
import logging
import sys
from rchain.client import RClient
from rchain.client import RClientException
import time
import subprocess

root = logging.getLogger()
root.setLevel(logging.DEBUG)

config_path = str(sys.argv[1])

ret=0
with grpc.insecure_channel('localhost:40401') as channel:
    client = RClient(channel)
    try:
        start_time = time.time()
        client.propose()
        dur = time.time() - start_time
        subprocess.run(['python3', 'reportInfluxDBMetric.py', 'pyrchain.proposetime', str(dur), config_path])
    except RClientException as e:
        # NoNewDeploys case should not exit with an error \
        # so autopropose script can deploy again before next propose
        if "NoNewDeploys" not in str(e):
            ret=1
sys.exit(ret)