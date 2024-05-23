#
# Columbia University - CSEE 4119 Computer Network
# Final Project
#
# blockchain.py -
#

import typing
import struct
import hashlib
import time
import json


def merkle(msgs: list[bytes]) -> bytes:
    """
    Computes Merkle tree root of arbitrary list of bytes objects.
    """
    n = len(msgs)

    if n == 0:
        return b""

    if n == 1:
        return hashlib.sha256(msgs[0]).digest()

    return hashlib.sha256(
        merkle(msgs[: n // 2]) + merkle(msgs[n // 2:])).digest()


class Block:
    def __init__(
        self,
        id: int = 0,
        timestamp: int = int(time.time()),
        difficulty: int = 3,  # number of leading zeros in hex
        merkle_hash: bytes = int(0).to_bytes(32, "big"),
        nonce: int = 0,
        prev_hash: bytes = int(0).to_bytes(32, "big"),
        data: bytes = b"",
    ):
        """
        Initialize blockchain block.

        arguments:
        id -- (uint32) height of block in tree
        timestamp -- (uint32) epoch time of when block was mined
        difficulty -- (uint32) number of 0s in hash when computing nonce
        merkle_hash -- (bytes[32]) hash of Merkle tree root for data
        nonce -- (uint32) nonce value used for showing proof-of-work
        prev_hash -- (bytes[32]) hash of previous node in blockchain
        """
        self.id = id
        self.timestamp = timestamp
        self.difficulty = difficulty
        self.merkle_hash = merkle_hash
        self.nonce = nonce
        self.prev_hash = prev_hash
        self.data = data

        self.hash = b""

    def to_dict(self) -> dict:
        """
        Helper function to dump relevant fields in Block to a dict().
        """
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "difficulty": self.difficulty,
            "merkle_hash": self.merkle_hash.hex(),
            "nonce": self.nonce,
            "prev_hash": self.prev_hash.hex(),
            "data": self.data.hex(),
        }

    def from_dict(self, d: dict) -> bool:
        """
        Initialize block values from dict.

        Returns whether Block values are valid.
        """
        try:
            self.id = d["id"]
            self.timestamp = d["timestamp"]
            self.difficulty = d["difficulty"]
            self.merkle_hash = bytes.fromhex(d["merkle_hash"])
            self.nonce = d["nonce"]
            self.prev_hash = bytes.fromhex(d["prev_hash"])
            self.data = bytes.fromhex(d["data"])

            if (
                self.id < 0
                or self.timestamp < 0
                or self.difficulty < 0
                or len(self.merkle_hash) != 32
                or self.nonce < 0
                or len(self.prev_hash) != 32
            ):
                return False
        except KeyError:
            return False

        return True

    def to_bytes(self) -> bytes:
        """
        Pack current block's values into bytes.
        """
        header_data = (
            self.id,
            self.timestamp,
            self.difficulty,
            self.merkle_hash,
            self.nonce,
            self.prev_hash,
            self.data,
        )
        return struct.pack(f"!III32sI32s{len(self.data)}s", *header_data)

    def compute_hash(self) -> bytes:
        header = self.to_bytes()
        return hashlib.sha256(header).digest()


class Node:
    def __init__(self, block: Block):
        self.block = block
        self.next: Node | None = None


class Blockchain:
    def __init__(self, initialize=True):
        """
        Initialize blockchain object, optionally loading from json
        """
        self.head = None
        self.tail = None

        if initialize:
            self.create_genesis_block()

    def to_json(self, indent: int = 0) -> str:
        """
        Convert entire blockchain to json format.
        """
        chain = []
        node = self.head

        while node is not None:
            chain.append(node.block.to_dict())
            node = node.next

        bc = {"blockchain": chain}

        return json.dumps(bc, indent=indent)

    def from_json(self, json_data: str) -> bool:
        """
        Helper function to initialize the blockchain from a provided json string.

        Returns whether inputted values are
        """
        bc = json.loads(json_data)["blockchain"]

        for node_dict in bc:
            # verify blockchain
            new_block = Block()
            if not new_block.from_dict(node_dict) or not self.add_block(
                new_block, new_block.compute_hash()
            ):
                return False

        return True

    def create_genesis_block(self):
        """
        A function to generate genesis block and appends it to the chain.
        The block has index 0, previous_hash as 0, and a valid hash.
        """
        genesis_block = Block(difficulty=0)
        genesis_block.hash = genesis_block.compute_hash()
        genesis_node = Node(genesis_block)
        self.head = genesis_node
        self.tail = genesis_node

    def add_block(self, block: Block, proof: bytes) -> bool:
        """
        Add the block to the chain after verification.
        Verification includes:
        - Checking if the proof is valid.
        - The previous_hash referred in the block and the hash of latest block
          in the chain match.
        """
        if (
            self.tail
            and (
                self.tail.block.hash != block.prev_hash
                or block.id != self.tail.block.id + 1
            )
            or not self.is_valid_proof(block, proof)
        ):
            return False

        # check if is genesis block
        if len(block.data) != 0:
            # validate merkle hash/data
            data = json.loads(block.data.decode())["data"]
            computed_merkle = merkle([json.dumps(r).encode() for r in data])

            if computed_merkle != block.merkle_hash:
                return False

        block.hash = proof
        new_node = Node(block)

        if not self.head:
            self.head = new_node
        if self.tail:
            self.tail.next = new_node
        self.tail = new_node

        return True

    def is_valid_proof(self, block: Block, block_hash: bytes) -> bool:
        """
        Check if block_hash is valid hash of block and satisfies
        the difficulty criteria.
        """
        return (
            block_hash.hex().startswith("0" * block.difficulty)
            and block_hash == block.compute_hash()
        )

    def proof_of_work(self, block: Block):
        """
        Mine different values of nonce to get a satisfying hash
        """
        block.nonce = 0
        computed_hash = block.compute_hash()

        while not computed_hash.hex().startswith("0" * block.difficulty):
            block.nonce += 1
            computed_hash = block.compute_hash()

    def get_last_block(self) -> Block:
        """
        Retrive last block
        """
        return self.tail.block if self.tail else None


if __name__ == "__main__":
    bc = Blockchain()

    start_time = time.time()

    for i in range(2):
        new_block = Block(
            id=i + 1,
            difficulty=2,
            prev_hash=bc.tail.block.compute_hash(),
            data=f"kevvivn{i}".encode(),
        )
        bc.proof_of_work(new_block)
        bc.add_block(new_block, new_block.compute_hash())

    new_bc = Blockchain(initialize=False)
    valid = new_bc.from_json(bc.to_json())

    if valid and new_bc.to_json() == bc.to_json():
        print(new_bc.to_json(2))

    node = new_bc.head
    while node is not None:
        print(node.block.data.decode())
        node = node.next
    print(f"Time taken: {time.time() - start_time}")
