#
# Columbia University - CSEE 4119 Computer Network
# Final Project
#
# network_utils.py -
#

import socket


def recvall(sock, size):
    """
    general function to recv complete message/chunk

    arguments:
    sock -- the socket connected to the server
    size -- the size in bytes of the expected message
    """
    chunks = []
    bufsize = 8192

    while size > 0:
        data = sock.recv(min(size, bufsize))
        if not data:
            return data
        chunks.append(data)
        size -= len(data)

    return b"".join(chunks)


if __name__ == "__main__":
    pass
