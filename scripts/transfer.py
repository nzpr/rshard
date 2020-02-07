import grpc
import logging
import sys
from argparse import ArgumentParser
from rchain.client import RClient
from rchain.vault import VaultAPI
from rchain.crypto import PrivateKey

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
root = logging.getLogger()
root.addHandler(handler)
root.setLevel(logging.INFO)

parser = ArgumentParser(description="Transfer rev to another vault")
parser.add_argument("-p", "--private-key", action="store", type=str, required=True, dest="private_key", help="private key of the sender vault")
parser.add_argument("-r", "--receiver", action="store", type=str, required=True, dest="receiver", help="receiver of the transfer")
parser.add_argument("-a", "--amount", action="store", type=int, required=True, dest="amount", help="the amount of the transfer")

args = parser.parse_args()
try:
    private_key = PrivateKey.from_hex(args.private_key)
except:
    logging.error("The private you provided is not valid")
    sys.exit(1)

with grpc.insecure_channel('localhost:40401') as channel:
    client = RClient(channel)
    vault = VaultAPI(client, private_key)
    vault.transfer(from_addr=None, to_addr=args.receiver, amount=args.amount)
    logging.info("Succeed transfer {} from {} to {} .".format(args.amount, private_key.get_public_key().get_rev_address(), args.receiver))
