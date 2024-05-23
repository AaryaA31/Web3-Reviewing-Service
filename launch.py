"""
One-stop script to set up and launch DVR process on multiple VMs!

Pre-requisites:
- Install paramiko and scp:
   pip install paramiko
   pip install scp
- Make sure SSH keys are added to each VM.
- SSH into each VM at least once prior to running this script so that the IPs will be added to the known_hosts file.
  If you don't do this, you will get an error saying <IP> not found in known_hosts

Notes:
- If you get the error "Host key for server '34.136.55.60' does not match: got ..., expected ...
  then you need to remove the entry for that IP in the known_hosts file (simply delete the line(s) corresponding to that IP)
  and re-add it to known_hosts by SSHing into the VM with that IP.
"""

from paramiko import SSHClient
from scp import SCPClient
import sys


uni = input("Enter your UNI/GitHub username: ")
key_filename = input("Enter the path to your SSH key: ")
vm_ex_ips_input = input(
    "Enter the external IPs of your VMs, separated by commas: ")
# Converts the string of IPs into a list
vm_ex_ips = vm_ex_ips_input.split(',')
tracker_ip = input("Enter the external IP of your tracker VM: ")
tracker_port = input("Enter the port of your tracker VM: ")
internal_port = input("Enter the internal port number: ")


external_port = 60000
#internal_port = xxxxxx


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    RESET = '\x1b[0m'


def load_files():
    try:
        ssh = SSHClient()
        ssh.load_system_host_keys()
        print(bcolors.OKBLUE + "SCPing files to VMs" + bcolors.RESET)
        for vm_ex_ip in vm_ex_ips:
            ssh.connect(vm_ex_ip, username=uni, key_filename=key_filename)
            with SCPClient(ssh.get_transport()) as scp:
                scp.put('src/peer.py', 'peer.py')
                scp.put('src/tracker.py', 'tracker.py')
                scp.put('src/network_utils.py', 'network_utils.py')
                scp.put('src/blockchain.py', 'blockchain.py')
                scp.put('src/review_client.py', 'review_client.py')
                scp.put('logo.png', 'logo.png')
                stdin, stdout, stderr = ssh.exec_command("chmod +x *")
            ssh.close()
    except KeyboardInterrupt:
        print(bcolors.OKBLUE + "Bye!" + bcolors.RESET)
        sys.exit()


def launch_peers(ip):
    ssh = SSHClient()
    ssh.load_system_host_keys()
    ssh.connect(ip, username=uni, key_filename=key_filename)
    ssh.exec_command(
        f"stdbuf -oL python3 peer.py {tracker_ip} {tracker_port} {internal_port}")
    ssh.close()


def launch_tracker(tracker_ip):
    ssh = SSHClient()
    ssh.load_system_host_keys()
    ssh.connect(tracker_ip, username=uni, key_filename=key_filename)
    ssh.exec_command(f"stdbuf -oL python3 tracker.py {tracker_port}")
    ssh.close()


if __name__ == "__main__":
    load_files()  # Load files to VMs
    launch_tracker(tracker_ip)
    for ip in vm_ex_ips:
        launch_peers(ip)
