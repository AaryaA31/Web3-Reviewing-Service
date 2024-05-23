# CSEE 4119 Spring 2024, Class Project - TESTING File
## Team name: localhost
## Team members (name, GitHub username):
- Aarya Agarwal (AaryaA31)
- Makram Bekdache (MakramB)
- Kevin Qiu (kzqiu)
- Louis Zheng (louis-zh)

To begin testing, please follow the guidelines in the README.txt

These are the VMs in this array just so you know the numbers:
![PNG image](https://github.com/csee4119-spring-2024/project-localhost/assets/100621994/3e12ed7e-1fb2-4df6-a0d2-8b3d17a87509)


After running the tracker and peer scrips,
With one tracker and 3 peers the tracker gives the following output once connected to the peers:
![PNG image](https://github.com/csee4119-spring-2024/project-localhost/assets/100621994/2ae17dbd-2954-4beb-9a5a-c222471607d0)

We see that the peers also receive the genesis block:
![PNG image](https://github.com/csee4119-spring-2024/project-localhost/assets/100621994/23295e65-f6c4-4bb6-be52-81c8a89c752b)

We added two extra peers to show that the tracker elegantly handled joining:
![Screenshot 2024-05-05 at 11 45 40 PM](https://github.com/csee4119-spring-2024/project-localhost/assets/100621994/ac863a91-ce39-4704-b0cf-2fb26572251a)

Now we had a peer leave and you can see the gracious exiting:
- Peer:![PNG image](https://github.com/csee4119-spring-2024/project-localhost/assets/100621994/6a8fccf2-e226-4c16-a5c7-8bf7b6c5d0d5)

The same peer reentered graciously:
- Tracker:![PNG image](https://github.com/csee4119-spring-2024/project-localhost/assets/100621994/e3f1d4a3-52c6-41f3-aa69-aca4779c3d49)
- You can see that the same peer has a new port since we changed it to avoid conflicts

Application demonstration using our GUI:
After properly launching the GUI by entered the tracker IP you see this:
![PNG image](https://github.com/csee4119-spring-2024/project-localhost/assets/100621994/9977fd61-0903-4a8e-87d2-eaedef2a6cc4)
We have an external IP field that you use to modify which peer you want to add the review on behalf of,

Adding our first review:
![PNG image](https://github.com/csee4119-spring-2024/project-localhost/assets/100621994/babb455c-0cb9-44db-93fe-4c53d4ad26e5)

This is the JSON view of the blockchain in the GUI after the node was added (click update first):
![PNG image](https://github.com/csee4119-spring-2024/project-localhost/assets/100621994/2784099d-96ca-4bab-875a-9c4d3bcb5253)

You can see the updates for each additional peer as well:
![PNG image](https://github.com/csee4119-spring-2024/project-localhost/assets/100621994/ac70f63c-6593-43e3-b97b-9eaab6927d51)

Now a second add from a different node, this shows successful broadcasting:
GUI side: ![PNG image](https://github.com/csee4119-spring-2024/project-localhost/assets/100621994/2b54821f-b874-474d-8411-95a2be7af5f1)
![PNG image](https://github.com/csee4119-spring-2024/project-localhost/assets/100621994/ea0d9a76-e4cb-4a82-93ec-61ffc0ee4889)

Peer side: 
![PNG image](https://github.com/csee4119-spring-2024/project-localhost/assets/100621994/679a413a-a94f-4ab0-b5f3-2a6e238c60d1)

We updated the block size to 2 reviews per block (we will show how during demo):
![PNG image](https://github.com/csee4119-spring-2024/project-localhost/assets/100621994/9dc631ed-f5f5-41bc-8c3e-d5070f68de69)
The one line of code that was changed is the last one in this ss of peer.py:
![PNG image](https://github.com/csee4119-spring-2024/project-localhost/assets/100621994/e8126d2b-84e8-488a-9ea3-a65c0a4bdb9f)





