[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-24ddc0f5d75046c5622901739e7c5dd533143b0c8e959d652212380cedb1ea36.svg)](https://classroom.github.com/a/-Lgd7v9y)
# CSEE 4119 Spring 2024, Class Project - README file
## Team name: localhost
## Team members (name, GitHub username):

- Aarya Agarwal (AaryaA31)
- Makram Bekdache (MakramB, some commits wrongfully committed under 'BuildTools' username)
- Kevin Qiu (kzqiu)
- Louis Zheng (louis-zh)

### Installation

```bash
# create a virtual env
$ python -m venv .venv

# activate the virtual env
$ source .venv/bin/activate

# install dependencies
$ pip install -r requirements.txt
```

### Blockchain - Peers and Tracker

We implemented a blockchain using a P2P network and an additional tracker server. For a single blockchain network, there is typically only one tracker and multiple peers, therefore our peers are designed to handle a single tracker connection.

```bash
$ cd src

# running the tracker
$ python tracker.py <listen_port>

# running a peer
$ python peer.py <tracker_ip> <tracker_port> <listen_port>
```

### Demo Application - Decentralized Review Messaging

We implemented an application on top of our blockchain, allowing users of the demo program to send reviews to an arbitrary number of peers. Each peer will save the reviews, adding the information to the blockchain once they receive a sufficient number of messages. By default, this number is set to only 1 for visibility and demonstration purposes but can be made dynamic to withstand high-traffic situations. 

```bash
$ cd src

# run streamlit demo (run this locally so that you can see the GUI)
$ streamlit run review_client.py

# if the default port 8501 is not forwarded, run this instead
$ sudo streamlit run review_client.py --server.port=80
```

### Additional Information

Make sure to do the following:
Add a Firewall rule that allowed connections from IP4 range: 0.0.0.0/0 in your GCP filewall settings

Please see the `DESIGN.md` and `TESTING.md` files for additional details.
