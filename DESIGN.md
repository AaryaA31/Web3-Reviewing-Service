# CSEE 4119 Spring 2024, Class Project - DESIGN File
## Team name: localhost
## Team members (name, GitHub username):
- Aarya Agarwal (AaryaA31)
- Makram Bekdache (MakramB)
- Kevin Qiu (kzqiu)
- Louis Zheng (louis-zh)

The objective of this project is to design a blockchain server and corresponding client programs, as well as an application that uses it. We discuss each individual component below:

### Application

Our application implements a decentralized review board. This concept is intended to safeguard freedom of speech, by avoiding censorship through the avoidance of central authority surveillance. Reviewers create reviews that are uploaded according to a specific data format to all the peers in the network. The peer will accumulate these reviews until it has enough data to fill a "block" of data, after which it will begin to mine the next block (unit of data) in the blockchain. Once a block is fully mined, the information is broadcast to the broader network.

### Blockchain Tracker

The tracker is an always-on server that stores information about the peers in the blockchain network. Its main task is to broadcast this information to all peers in a periodic and event-based manner (e.g. peers joining or leaving). To handle multiple connections, we must:

- maintain a main waiting thread for new connections,
- spawn new threads for each new peer joining the network,
- maintain a locked (mutexed) list of connected peers with a list of IP addresses.

The tracker doesn't keep track of any other information, and doesn't hold the actual blockchain data. 

### Blockchain Peer

The peers in a network are individual machines joining a network. They maintain local blockchains, and must handle mining, broadcasting, and verification of blocks. They periodically send a request for an updated list of peers from the tracker. They will also preemptively send such a request whenever they are about to broadcast a new block. Furthermore, they locally maintain data related to the blockchain, which can be used by our application. This data is encoded via a Merkle tree hash, included in each block. Regarding mining, whenever each peer has accumulated enough messages in its backlog (defined by the variable `self.reviews_per_block` and defaulted to 1), the peer begins trying nonce values to mine the block. Once it has completed the proof-of-work, the peer will then finally broadcast the newly mined block to the rest of the network.

To handle the different messages, we spawn three additional threads:
- The main thread handles the TCP connection with the tracker and periodically receives updates about available peers.
- The receiving thread handles incoming UDP messages and adds them to a message queue (defined as `self.message_queue`).
- The sending thread handles UDP messages to be sent to other peers or clients stored in the send queue (defined as `self.send_queue`).
- The message thread reads from the message queue and performs logic depending on the message type, and it also consumes reviews received from clients and adds to the blockchain if needed via `self.data_queue` and `self.consume_data()`.

### Block Header

The header design for our blockchain is similar to that of Bitcoin. For data transmission purposes in our application, we encode both the individual blocks and the entire blockchain in JSON format.

```text
Header (76 bytes):
block_id    - uint_32  (4 bytes)
  - Measures the depth of a given block within the blockchain tree. Used to measure the lenght of branches when forking occurs.
time        - uint_32  (4 bytes)
  - The block time is a Unix epoch time marking when the miner started hashing the header (according to the miner).
    Must be strictly greater than the median time of the previous 11 blocks.
    Full nodes will not accept blocks with headers that are two hours ahead (in the future) of their internal clock.
prev_hash   - char[32] (32 bytes)
  - A SHA256(SHA256()) hash in internal byte order of the previous block’s header.
    This ensures no previous block can be changed without also changing this block’s header
merkle_hash - char[32] (32 bytes)
  - A SHA256(SHA256()) hash in internal byte order.
    The merkle root is derived from the hashes of all transactions included in this block, ensuring that none of those 
    transactions can be modified without modifying the header.
difficulty  - uint_32  (4 bytes)
  - An encoded version of the target threshold this block’s header hash must be less than or equal to. Refer to Bitcoin's nBits documentation.
nonce       - uint_32  (4 bytes)
  - An arbitrary number changed by miners. Used to modify the header hash in order to produce a hash less than, or equal to the target threshold.
    If all 32-bit values are tested, the time can be updated, or the coinbase transaction can be changed and the merkle root updated.
```

We also include an additional data field, which is of arbitrary size.

### Block Size

Each peer has a messages per block flag that can be set according to our use. It is left to 1 in our demonstration for practical purposes.

### Fork Handling

To handle forks, blocks received at the same height are ignored. In cases of fast forwarding: receiving a block that has id > current tail id + 1, we instead request the whole blockchain and set to that if its valid. The same mechanism is used when a new peer joins the network, where it randomly select another peer to request the entire blockchain.

### Merkle Tree Hash

To secure our blocks, we employ a Merkle Tree hash. 

- The algorithm pairs up adjacent blocks and hashes them together, starting at the "leaf" bottom blocks, up to the "genesis" or root block. Eech pair of hashes is concatenated and hashed again until a single hash, known as the Merkle root, is obtained at the top of the tree.

- When a node in the blockchain receives a new block, it can verify the integrity of the transactions by recalculating the Merkle root using the transactions' hashes provided in the block header. 

### Dynamic Difficulty Adjustement

The difficulty factor used to compute the hash varies in our code according to the peers connected to the network, i.e it increases if the available computing power also increases.

### Demo infrastructure

To demonstrate our application, we built a demo client on the streamlit, a Python framework that allowed us to build a effective proof-of-concept to showcase our work. 

<img width="1512" alt="Screenshot 2024-05-05 at 1 14 50 AM" src="https://github.com/csee4119-spring-2024/project-localhost/assets/134444360/2826a43a-4934-446b-a89e-26c91ad22edc">

The application requires the user to set configuration parameters:
- Tracker IP: The IP address of the blockchain tracking server.
- Tracker Port: The network port corresponding to the blockchain tracking server.

<img width="1505" alt="Screenshot 2024-05-05 at 1 21 02 AM" src="https://github.com/csee4119-spring-2024/project-localhost/assets/134444360/ddd61eef-04b1-430c-8c42-011cf6fa894d">

- After entering the appropriate configuration information, the user can update the peer list, and will be presented with a list of selectable peers.
- A review form field opens up on the webpage, where the user can enter the following their username, subject, a 0-5 numerical rating, and a text review.

<img width="1498" alt="Screenshot 2024-05-05 at 1 24 45 AM" src="https://github.com/csee4119-spring-2024/project-localhost/assets/134444360/34edfcb1-6397-406a-b79f-d5f4ef9eb2ab">

- Submitting a review will show a preview on the right-hand side of the page (please click the update button on the upper-right corner to update this view). This window will show all review form fields (username, rating...) along with the blockchain metadata which includes the assigned block ID, difficulty, and nonce value.

<img width="1426" alt="Screenshot 2024-05-05 at 1 28 26 AM" src="https://github.com/csee4119-spring-2024/project-localhost/assets/134444360/ea743cdb-c157-44dc-8030-8f7ca97fde51">

- The user can also view blockchain information in JSON form, which includes the actual merkle hash, and previous hash informations, both useful for the purposes of this tech demo.

### Bonus 
- We created a cute mascot for this project! Hope you like our logo:

![DALL·E 2024-05-05 01 50 07 - Refine the abstract logo themed around 'local host', removing any unreadable text at the bottom  The logo features a qubit mascot, using Columbia Blue](https://github.com/csee4119-spring-2024/project-localhost/assets/134444360/671aa2e1-3cec-45df-9d60-0eaa4f1ee695) 

### References
- [MIT: How Blockchain Works](http://blockchain.mit.edu/how-blockchain-works)
- [Nakamoto, Satoshi, Bitcoin: A Peer-to-Peer Electronic Cash System](https://bitcoin.org/bitcoin.pdf)
- [Bitcoin Developer Reference - Blockchain](https://developer.bitcoin.org/reference/block_chain.html)
