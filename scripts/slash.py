import grpc
import logging
import sys
import random
import string
import json
from pathlib import Path
from argparse import ArgumentParser
from rchain.client import RClient
from rchain.certificate import get_node_id_raw
from rchain.crypto import
from cryptography.hazmat.backends import default_backend
from rchain.crypto import PrivateKey
import hashlib
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from rchain.pb.routing_pb2 import (
    Header,
    Node,
    Packet,
    Protocol,
    TLRequest,
)
from rchain.pb.DeployServiceCommon_pb2 import LightBlockInfo
from rchain.pb.CasperMessage_pb2 import BlockMessageProto, HeaderProto, BodyProto, RChainStateProto, BondProto
from rchain.pb.routing_pb2_grpc import (
    TransportLayerStub,
)

def random_bytes():
    return "".join(random.choices(string.ascii_letters, k=10)).encode('utf8')

def generate_hash() -> bytes:
    blake = hashlib.blake2b(digest_size=32)
    blake.update(random_bytes())
    return blake.digest()

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
root = logging.getLogger()
root.addHandler(handler)
root.setLevel(logging.INFO)

DEFAULT_KEY_FILE = "/var/lib/rnode/node.key.pem"
DEFAULT_CERT_FILE = "/var/lib/rnode/node.certificate.pem"
TESTNET_NODE_DIR = "/opt/rchain-testnet-node"
DEFAULT_CONFIG_FILE = "/var/lib/rnode/rnode.conf"

parser = ArgumentParser(description="Create an invalid block to slash a validator")
parser.add_argument("-p", "--target-node", action="store", type=str, required=True, dest="target_node",
                    help="the target of the invalid block send to")
parser.add_argument("-n", "--network-id", action="store", type=str, required=True, dest="network_id",
                    help="the network id of the network")
parser.add_argument("-t", "--target-net", action="store", type=str, required=True, dest="target_net",
                    help="target network you want to slash")

args = parser.parse_args()
target_node = args.target_node
target_net = args.target_net
network_id = args.network_id

local_cert = Path(DEFAULT_CERT_FILE).read_bytes()
local_node_key = Path(DEFAULT_KEY_FILE).read_bytes()
private_key = load_pem_private_key(local_node_key, password=None, backend=default_backend())
node_id = get_node_id_raw(private_key)
node_pb = Node(id=node_id, host="", tcp_port=40404, udp_port=40440)
header = Header(sender=node_pb, networkId=network_id)

target_node_cert = Path("{}/node-files.{}/{}/node.certificate.pem".format(TESTNET_NODE_DIR, target_net, target_node)).read_bytes()
target_node_key = Path("{}/node-files.{}/{}/node.key.pem".format(TESTNET_NODE_DIR, target_net, target_node)).read_bytes()
target_node_private_key = load_pem_private_key(target_node_key, password=None, backend=default_backend())

credential = grpc.ssl_channel_credentials(target_node_cert, local_node_key, local_cert)

config = json.loads(Path(DEFAULT_CONFIG_FILE).read_text())
bonded_private_key = PrivateKey.from_hex(config['rnode']['casper']['validator-private-key'])

def get_the_latest_block():
    with grpc.insecure_channel("{}.{}.rchain-dev.tk:40404".format(target_node, target_net)) as g_channel:
        client = RClient(g_channel)
        blockList = client.show_blocks(1)

        latest_block = blockList[0]

        return latest_block


def generate_invalid_block(from_block: LightBlockInfo):
    state_proto = RChainStateProto(
        preStateHash=bytes.fromhex(from_block.preStateHash),
        postStateHash=bytes.fromhex(from_block.postStateHash),
        blockNumber= from_block.blockNumber+1,
        bonds=[BondProto(validator=bytes.fromhex(bond.validator), stake=bond.stake) for bond in from_block.bonds]
    )
    header_proto = HeaderProto(
        parentsHashList=[bytes.fromhex(parent) for parent in from_block.parentsHashList],
        timestamp=1,
        version=1,
        extraBytes=b""
    )
    body_proto = BodyProto(
        state=state_proto,
        deploys=[]
    )
    block_hash = generate_hash()
    return BlockMessageProto(
        blockHash = generate_hash(),
        header = header_proto,
        body = body_proto,
        justifications=[],
        sender=bonded_private_key.get_public_key().to_bytes(),
        seqNum=from_block.seqNum,
        sig=bonded_private_key.sign_block_hash(block_hash),
        sigAlgorithm="secp256k1",
        shardId="rchain",
        extraBytes=b""
    )

latest_block = get_the_latest_block()

with grpc.secure_channel("{}.{}.rchain-dev.tk:40400".format(target_node, target_net),
                         credential,
                         options=(
                                 ('grpc.ssl_target_name_override', get_node_id_raw(target_node_private_key).hex()),)
                         ) as channel:
    stub = TransportLayerStub(channel)
    block = generate_invalid_block(latest_block)
    block_msg_packet = Packet(typeId="BlockMessage", content=block.SerializeToString())
    protocol = Protocol(header=header, packet=block_msg_packet)
    request = TLRequest(protocol=protocol)
    stub.Send(request)
