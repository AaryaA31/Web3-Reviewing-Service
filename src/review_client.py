#
# Columbia University - CSEE 4119 Computer Network
# Final Project
#
# review_client.py -
#

import streamlit as st
import socket
import time
from network_utils import *
from blockchain import *

# Initialize session state variables if not already set
if "peerlist" not in st.session_state:
    st.session_state.peerlist = None
    st.session_state.peer = None
    st.session_state.bc = Blockchain(initialize=False)

# Set the layout of the Streamlit page to wide
st.set_page_config(layout="wide")

# Create layout columns for title and logo
col1, col2 = st.columns([0.9, 0.1])

# Display the application title
with col1:
    st.title("_Demo_: :rainbow: [Decentralized] Review System")

# Display the application logo
with col2:
    st.image("logo.png", caption="By localhost", width=120)
st.divider()

# Tracker IP and port input form
with st.form(key="tracker_data"):
    tracker_ip = st.text_input("Tracker IP", value="127.0.0.1")
    tracker_port = st.number_input(
        "Tracker Port",
        value=50000,
        placeholder="(49152 - 65535)",
        min_value=49152,
        max_value=65535,
        step=1,
    )

    tracker_submit = st.form_submit_button("Update Peers")

    # If the form is submitted, connect to the tracker and retrieve peer list
    if tracker_submit:
        tracker_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tracker_sock.connect((tracker_ip, int(tracker_port)))

        tracker_sock.sendall((0).to_bytes(4, byteorder="big"))
        nbytes = int.from_bytes(recvall(tracker_sock, 4), byteorder="big")
        msg = recvall(tracker_sock, nbytes).decode()
        tracker_sock.close()

        # Parse peer information from tracker response
        if len(msg) != 0:
            peers = [a.split(":") for a in msg.split(";")]
            st.session_state.peerlist = [tuple((p[0], int(p[1]))) for p in peers]

# Allow user to select a peer from the list or manually enter peer details
if st.session_state.peerlist:
    peer = st.radio("Select peer", st.session_state.peerlist, horizontal=True)

    custom_peer_cols = st.columns(2)

    with custom_peer_cols[0]:
        custom_peer_ip = st.text_input("Custom Peer (External IP)")
    with custom_peer_cols[1]:
        custom_peer_port = st.number_input(
            "Custom Peer Port",
            value=60000,
            placeholder="(49152 - 65535)",
            min_value=49152,
            max_value=655335,
            step=1,
        )

    # Update the selected peer based on user input
    if custom_peer_ip != "":
        st.session_state.peer = (custom_peer_ip, int(custom_peer_port))
    else:
        st.session_state.peer = peer

    st.write(st.session_state.peer)

# Review submission form and handling
if st.session_state.peer is not None:
    col1, col2 = st.columns(2)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    with col1:
        st.markdown("### Review Form")

        with st.form(key="review_form", clear_on_submit=True):
            reviewer = st.text_input("User Name")
            review_subject = st.text_input("Subject")
            rating = st.slider(
                "Rating", min_value=0.0, max_value=5.0, value=2.5, step=0.5
            )
            review_body = st.text_area("Body")
            submit = st.form_submit_button()

            # If form is submitted, encode and send review data to selected peer
            if submit:
                data = {
                    "user": reviewer,
                    "subject": review_subject,
                    "rating": rating,
                    "body": review_body,
                    "time": int(time.time()),
                }

                encoded_msg = json.dumps(data).encode()

                # Sending message length and message itself over UDP
                sock.sendto(
                    (8 + len(encoded_msg)).to_bytes(4, byteorder="big"),
                    st.session_state.peer,
                )
                sock.sendto(
                    struct.pack(f"!I{len(encoded_msg)}s", 1, encoded_msg),
                    st.session_state.peer,
                )

                sock.settimeout(5)

                try:
                    msglen, _ = sock.recvfrom(4)
                    msg, _ = sock.recvfrom(
                        int.from_bytes(msglen, byteorder="big"))
                    if msg is not None:
                        st.success("Success: Review submitted!")
                    else:
                        st.error("Error: Empty response!")
                except socket.timeout:
                    st.error("Error: Socket timed out (invalid peer or busy)!")

                sock.settimeout(None)

    # Blockchain and review display section
    with col2:
        subcols = st.columns([7, 1])
        with subcols[0]:
            st.markdown("### Reviews")

        with subcols[1]:
            update_bc = st.button("Update")

        # Request blockchain updates from peer
        if update_bc:
            st.session_state.bc = Blockchain(initialize=False)

            sock.sendto(
                (4).to_bytes(4, byteorder="big"), st.session_state.peer)
            sock.sendto((0).to_bytes(4, byteorder="big"), st.session_state.peer)

            sock.settimeout(5)

            try:
                msglen, _ = sock.recvfrom(4)
                msg, _ = sock.recvfrom(int.from_bytes(msglen, byteorder="big"))

                if st.session_state.bc.from_json(msg[4:].decode()):
                    print("Decoded blockchain successfully.")
                else:
                    print("Could not decode blockchain.")
            except socket.timeout:
                st.error("Error: Socket timed out (invalid peer or busy)!")

            sock.settimeout(None)

        # Display reviews from the blockchain
        if st.session_state.bc:
            node = st.session_state.bc.head

            review_data = []

            while node is not None:
                if node.block.id == 0:
                    node = node.next
                    continue

                block_data = json.loads(node.block.data.decode())["data"]

                for review in block_data:
                    review_data.append((node.block.to_dict(), review))

                node = node.next

            review_data.reverse()

            for block_review in review_data:
                metadata, review = block_review
                container = st.container(border=True)
                curtime = time.strftime(
                    "%Y-%m-%d %H:%M:%S", time.localtime(float(review["time"]))
                )
                container.markdown(f"#### {review['subject']}")
                container.markdown(f"**{review['user']}** :gray[· {curtime}]")
                container.write(f"Rating: {review['rating']}")
                container.write(review["body"])
                container.write(
                    f":gray[Metadata - Block ID: {metadata['id']} · difficulty: {metadata['difficulty']} · nonce: {metadata['nonce']}]"
                )

    st.header("Blockchain")
    st.json(st.session_state.bc.to_json(), expanded=False)
