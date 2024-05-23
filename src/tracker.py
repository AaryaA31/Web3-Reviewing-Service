#
# Columbia University - CSEE 4119 Computer Network
# Final Project
#
# tracker.py -
#

import socket
import threading
import argparse
import errno
import struct
from blockchain import *
from network_utils import *
import sys
import signal


class Tracker:
    def __init__(self, port):
        """
        Initialize Tracker server.

        arguments:
        port -- port for the tracker server to bind to.
        the dicts here are used later on for logging purposes
        """
        self.port = port
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.lock = threading.Lock()
        # dict of (ip, port): client_sock
        self.connections = {}
        # dict of (ip, bind port): (ip, recv port)
        self.bind_to_recv = {}

        try:
            self.server_sock.bind(("", port))
        except socket.error as e:
            if e.errno == errno.EADDRINUSE:
                print("Port is already in use")
                exit(1)

        self.server_sock.listen()

    def peer_thread(self, client_sock, client_addr):
        """
        Handle new messages from a peer in a separate thread.

        arguments:
        client_sock -- the socket connected to the peer.
        """
        client_sock.settimeout(5)

        while True:
            # wait for request from client
            # 1. handle request for current list of peers
            # 2. handle peer leaving, broadcast updated list
            try:
                msg = recvall(client_sock, 4)

                if not msg:
                    # remove thread from list and connection
                    # broadcast to all
                    del self.connections[self.bind_to_recv[client_addr]]
                    del self.bind_to_recv[client_addr]
                    self.broadcast()
                    break
            except socket.timeout:
                pass

            # otherwise handle request
            self.send_connections([client_sock])

        client_sock.close()

    def run(self):
        """
        Run the tracker server.
        """
        self.server_sock.settimeout(3)
        try:
            while True:
                try:
                    # wait for connection
                    client_sock, client_addr = self.server_sock.accept()

                    msglen = int.from_bytes(
                        recvall(client_sock, 4), byteorder="big")

                    if msglen == 0:
                        print("Received client request.")
                        self.send_connections([client_sock])
                        client_sock.close()
                        continue

                    addr = recvall(client_sock, msglen).decode().split(":")
                    # on accepting connection, send current list of connections
                    # also spin up a new thread to handle this
                    self.lock.acquire()
                    self.bind_to_recv[client_addr] = (addr[0], int(addr[1]))
                    self.connections[(addr[0], int(addr[1]))] = client_sock
                    threading.Thread(
                        target=self.peer_thread, args=(
                            client_sock, client_addr)).start()
                    self.broadcast()

                    print(self.connections.keys())

                    self.lock.release()

                except socket.timeout:
                    self.broadcast()
        finally:
            self.close()

    def broadcast(self):
        """
        Send connection list to all peers.
        """
        self.send_connections(self.connections.values())

    def send_connections(self, sock_list):
        """
        Only call this function when the connections list is locked.
        """
        peerlist = ";".join(
            [f"{a[0]}:{a[1]}" for a in self.connections.keys()]
        ).encode()
        msg = struct.pack("!I", len(peerlist)) + peerlist

        for sock in sock_list:
            sock.sendall(msg)

    def close(self):
        """
        Close all client sockets and the server socket.
        """
        print("Shutting down the tracker...")
        self.lock.acquire()
        for client_sock in self.connections.values():
            client_sock.close()
        self.server_sock.close()
        self.lock.release()
        print("Tracker shut down successfully.")


def signal_handler(sig, frame):
    """
    Gracefully handles user Ctrl+C/Cmd+C input to terminate.
    """
    global tracker
    tracker.close()
    sys.exit(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="tracker.py", description="Blockchain tracking server."
    )
    parser.add_argument(
        "listen_port",
        type=int,
        choices=range(49152, 65535),
        metavar="listen_port: (49152 - 65535)",
    )
    args = parser.parse_args()

    # init Tracker Server and begin listening
    tracker = Tracker(args.listen_port)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    tracker.run()
