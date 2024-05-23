#
# Columbia University - CSEE 4119 Computer Network
# Final Project
#
# peer.py -
#

import socket
import argparse
import threading
import errno
import sys
import signal
import random
from queue import Queue
from blockchain import *
from network_utils import *


class Peer:
    def __init__(self, tracker_ip, tracker_port, recv_port):
        """
        Initialize Peer.

        arguments:
        tracker_ip -- ip of tracker server
        tracker_port -- port of tracker server
        recv_port -- port of peer server to receive messages
        """
        self.tracker_ip = tracker_ip
        self.tracker_port = tracker_port

        self.chain = None
        self.peerlist = []
        self.message_queue = Queue()
        self.send_queue = Queue()
        self.data_queue = Queue()
        self.blockchain = Blockchain(initialize=False)
        self.reviews_per_block = 1

        self.ip = socket.gethostbyname(socket.gethostname())
        self.port = recv_port
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        try:
            self.server_sock.bind(("", recv_port))
        except socket.error as e:
            if e.errno == errno.EADDRINUSE:
                print("Port is already in use")
                exit(1)

    #### TCP implementation ####
    def recv_peerlist(self):
        """
        Wait to receive a peer list and parse.
        """
        nbytes = int.from_bytes(recvall(self.tracker_sock, 4), byteorder="big")
        msg = recvall(self.tracker_sock, nbytes).decode()

        # List of (ip, port) of peers
        peers = [a.split(":") for a in msg.split(";")]
        self.peerlist = [tuple((p[0], int(p[1]))) for p in peers]

    #### TCP implementation ####
    def connection_thread(self):
        """
        Connect to tracker server and handle updated peer lists.
        """
        while True:
            self.recv_peerlist()

    #### UDP implementation ####
    def recv_handler(self, sock):
        """
        receiver handler thread/function

        Each message has the format:
        length (not saved)   - 4 bytes
        message type (saved) - 4 bytes
        message (saved)      - (length - 4) bytes
        """
        while True:
            msg_len, addr = sock.recvfrom(4)
            message, addr = sock.recvfrom(
                int.from_bytes(msg_len, byteorder="big"))
            self.message_queue.put((message, addr))

    #### UDP implementation ####
    def send_handler(self):
        while True:
            while self.send_queue.qsize() != 0:
                # broadcast to all peers
                msg, addrs = self.send_queue.get()

                for addr_port in addrs:
                    if addr_port == tuple((self.ip, self.port)):
                        continue
                    self.server_sock.sendto(
                        len(msg).to_bytes(4, byteorder="big"), addr_port
                    )
                    self.server_sock.sendto(msg, addr_port)

    #### UDP implementation ####
    def message_handler(self):
        """
        Procecess buffered messages

        Types of messages can be:
        0. [Peer/Client] Full blockchain request
        1. [Client] Submission of review
        2. [Peer] Receive new Block
        3. [Peer] Receive entire Blockchain
        """
        while True:
            # first check if there are reviews to add to the blockchain
            self.consume_data()

            # then consume messages in queue
            while self.message_queue.qsize() != 0:
                message, addr = self.message_queue.get()
                msg_type = int.from_bytes(message[:4], byteorder="big")

                if msg_type == 0:
                    # respond to request for full blockchain
                    bc = self.blockchain.to_json().encode()
                    msg = struct.pack(f"!I{len(bc)}s", 3, bc)
                    self.send_queue.put((msg, [addr]))

                elif msg_type == 1:
                    # received new review, add to queue
                    self.data_queue.put(message[4:])
                    self.send_queue.put(
                        ((0).to_bytes(4, byteorder="big"), [addr]))

                elif msg_type == 2:
                    # handle new block, if it can be directly added, do that
                    # otherwise, send request for entire blockchain
                    # if it is at the same height and is valid, just ignore it!
                    new_block = Block()
                    if new_block.from_dict(json.loads(message[4:])):
                        # simulated loss: testing if choosing longest chain works (type 3)
                        # if new_block.id % 2 == 1:
                        #     continue

                        if new_block.id == self.blockchain.tail.block.id:
                            pass  # ignore fork
                        if new_block.id > self.blockchain.tail.block.id + 1:
                            self.send_queue.put(
                                ((0).to_bytes(4, byteorder="big"), [addr])
                            )
                        elif self.blockchain.add_block(
                            new_block, new_block.compute_hash()
                        ):
                            print(self.blockchain.to_json(2))
                        else:
                            print("Invalid block received.")

                elif msg_type == 3:
                    new_bc = Blockchain(initialize=False)
                    if new_bc.from_json(message[4:].decode()):
                        if new_bc.tail.block.id > self.blockchain.tail.block.id:
                            self.blockchain = new_bc

                        print(self.blockchain.to_json(2))

    def consume_data(self):
        """
        This function consumes reviews from the data queue to form new blocks when sufficient reviews are gathered.
        It creates blocks with a proof-of-work mechanism, and if successful, broadcasts them to peers.
        Unsuccessful attempts result in reviews being re-queued.
        """

        if self.data_queue.qsize() >= self.reviews_per_block:
            reviews = [self.data_queue.get()
                       for _ in range(self.reviews_per_block)]
            merkle_root = merkle(reviews)
            data = {"data": [json.loads(r.decode()) for r in reviews]}
            new_block = Block(
                id=self.blockchain.tail.block.id + 1,
                timestamp=int(time.time()),
                difficulty=len(self.peerlist),
                merkle_hash=merkle_root,
                prev_hash=self.blockchain.tail.block.compute_hash(),
                data=json.dumps(data).encode(),
            )
            self.blockchain.proof_of_work(new_block)

            if not self.blockchain.add_block(
                    new_block, new_block.compute_hash()):
                print("Failed")
                for r in reviews:
                    self.data_queue.put(r)
                return

            print(self.blockchain.to_json(2))

            block_data = json.dumps(new_block.to_dict()).encode()
            msg = struct.pack(f"!I{len(block_data)}s", 2, block_data)

            self.send_queue.put((msg, self.peerlist))

    def run(self):
        """
        Run the peer.
        """
        # connect to tracker and get peer list to see if there is already a
        # blockchain
        self.tracker_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tracker_sock.connect((self.tracker_ip, self.tracker_port))
        host_addr = f"{self.ip}:{self.port}"
        self.tracker_sock.sendall(len(host_addr).to_bytes(4, byteorder="big"))
        self.tracker_sock.sendall(host_addr.encode())
        self.recv_peerlist()

        # choose random peer from list for blockchain besides (itself)
        if len(self.peerlist) != 1:
            while True:
                peer = self.peerlist[random.randint(0, len(self.peerlist) - 2)]

                # request blockchain from peer
                self.server_sock.sendto(
                    (4).to_bytes(4, byteorder="big"), peer
                )  # length
                self.server_sock.sendto(
                    (0).to_bytes(4, byteorder="big"), peer
                )  # request type

                msglen, _ = self.server_sock.recvfrom(4)
                msg, _ = self.server_sock.recvfrom(
                    int.from_bytes(msglen, byteorder="big")
                )

                if self.blockchain.from_json(msg[4:].decode()):
                    print(self.blockchain.to_json(2))
                    break

        else:
            self.blockchain.create_genesis_block()

        recv_thread = threading.Thread(
            target=self.recv_handler, args=(self.server_sock,)
        )
        recv_thread.start()

        msg_thread = threading.Thread(target=self.message_handler)
        msg_thread.start()

        send_thread = threading.Thread(target=self.send_handler)
        send_thread.start()

        # Main thread handles connection to tracker
        self.connection_thread()

    def close(self):
        """
        Close the server socket
        """
        print("Shutting down the peer...")
        self.server_sock.close()
        self.tracker_sock.close()
        print("Peer shut down successfully.")


def signal_handler(sig, frame):
    """
    Gracefully handle Ctrl+C/Cmd+C user inputs
    """
    global peer
    peer.close()
    sys.exit(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="peer.py", description="Blockchain peer.")
    parser.add_argument("tracker_ip")
    parser.add_argument(
        "tracker_port",
        type=int,
        choices=range(49152, 65535),
        metavar="tracker_port: (49152 - 65535)",
    )
    parser.add_argument(
        "recv_port",
        type=int,
        choices=range(49152, 65535),
        metavar="recv_port: (49152 - 65535)",
    )
    args = parser.parse_args()

    peer = Peer(args.tracker_ip, args.tracker_port, args.recv_port)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    peer.run()
