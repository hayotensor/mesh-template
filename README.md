## Hypertensor subnet framework
[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)
A framework for building open & decentralized AI projects

---
This includes all the core components required to launch a decentralized AI application, including:
- **[Kademlia DHT (KAD-DHT)][bittorrent]** – for scalable, decentralized storage, routing, and communication
- **Asyncio-based DHT Node** – designed for fast, concurrent communications
- **DHT Protocol** – allows DHT nodes to request keys/neighbors from other DHT nodes, and manages routing tables
- **DHT Record Storage** – decentralized key-value storage with support for versioned and validated records with customizable predicate extensions
- **Record Validators** – attach custom validation logic to any stored record, such as key authentication and Pydantic schemas
- **DHT Traversal Tools** – Traverse the DHT graph
- **Routing Tables** – manage network topology and neighbor nodes. A data structure that contains DHT peers bucketed according to their distance to node_id. Follows Kademlia routing table
- **P2P Servicer Base** – register RPC methods to the DHT for nodes to call on one another with security authorizer extensions
- **Proof-of-Stake Integration** – incentivize and secure participation, i.e. must be staked to join the subnet
- **Hypertensor Consensus** – Ready to run in parallel to the Hypertensor consensus mechanism
- **Substrate Integration** – Connect to Hypertensor with an RPC endpoint
- **Secure Communication** – support for Ed25519 and RSA authentication for communication
- **Mock Local Database** – Test locally with a mocked database

> 💡 **Focus on Logic, Not Plumbing**
> The networking, cryptography, consensus, and storage layers are already handled. As a subnet builder, your only responsibility is to implement the application logic — the custom AI protocols and behaviors that live on top of the DHT.

## Full Documentation

https://docs.hypertensor.org

## Installation From source

### From source

To install this container from source, simply run the following:

```
git clone https://github.com/hypertensor-blockchain/mesh.git
cd mesh
python -m venv .venv
source .venv/bin/activate
pip install .
```

If you would like to verify that your installation is working properly, you can install with `pip install .[dev]`
instead. Then, you can run the tests with `pytest tests/`.

By default, the contatiner uses the precompiled binary of
the [go-libp2p-daemon](https://github.com/hypertensor-blockchain/go-libp2p-daemon) library. If you face compatibility issues or want to build the binary yourself, you can recompile it by running `pip install . --global-option="--buildgo"`.

Before running the compilation, please ensure that your machine has a recent version
of [Go toolchain](https://golang.org/doc/install) (1.15 or 1.16 are supported).

### System requirements

- __Linux__ is the default OS for which the container is developed and tested. We recommend Ubuntu 18.04+ (64-bit), but
  other 64-bit distros should work as well. Legacy 32-bit is not recommended.
- __macOS__ is partially supported.
  If you have issues, you can run the container using [Docker](https://docs.docker.com/desktop/mac/install/) instead.
  We recommend using [our Docker image](https://hub.docker.com/r/hypertensor-blockchain/mesh).
- __Windows 10+ (experimental)__ can run the container
  using [WSL](https://docs.microsoft.com/ru-ru/windows/wsl/install-win10). You can configure WSL to use GPU by
  following sections 1–3 of [this guide](https://docs.nvidia.com/cuda/wsl-user-guide/index.html) by NVIDIA. After
  that, you can simply follow the instructions above to install with pip or from source.

---

# Documentation

## .env
Create an `.env` file for the environmental variables.
```
touch .env
```
Fill out the `.env` file with the necessary variables from `.env.example`.

## Keys

There are 3 key types each node will need, a coldkey (blockchain account), a hotkey (blockchain account), and peer IDs (subnet identity).

The template currently allows RSA and Ed25519 key types and is interoperable between the two.

#### Generate coldkey (if needed)

#### Generate hotkey
- This is the hotkey of the node. It is used for validating and attesting only. Each hotkey is unique to each subnet node and no hotkey can be used twice.

#### Generate peer private keys

  - This will create 3 private key files for your peer
      - `peer_id`: Main peer ID for communication and signing
      - `bootstrap_peer_id`: (Optional usage) Peer ID to be used as a bootstrap node.
      - `client_peer_id`: (Optional usage) Peer ID to be used as a client. This is for those who want to build frontends to interact with the subnet.

The `bootstrap_peer_id` and `client_peer_id` are not required to be used as a peer, but they are required to be generated and stored on-chain when registering a node.

<b>Example Private Key Generation</b>

<b>RSA:</b>
```bash
keygen \
--path rsa-pk.key \
--bootstrap_path rsa-bootstrap-pk.key \
--client_path rsa-client-pk.key  \
--key_type rsa
```

<b>Ed25519:</b>
```bash
keygen \
--path ed-pk.key \
--bootstrap_path ed-bootstrap-pk.key \
--client_path ed-client-pk.key  \
--key_type ed25519
```

## Register and Activate Subnet Node (on-chain)

#### Register & Stake on Hypertensor
  - Call `register_subnet_node`
  - Retrieve your `start_epoch` by querying your SubnetNodesData storage element on polkadot.js with your subnet node ID. This is the epoch you must activate your node on + the grace period

##### Example Register & Stake CLI
```bash
register-node \
--subnet_id 1 \
--hotkey 0x773539d4Ac0e786233D90A233654ccEE26a613D9 \
--peer_id QmTJ8uyLJBwVprejUQfYFAywdXWfdnUQbC1Xif6QiTNta9 \
--bootnode_peer_id QmSjcNmhbRvek3YDQAAQ3rV8GKR8WByfW8LC4aMxk6gj7v \
--client_peer_id QmSjcNmhbRvek3YDQAAQ3rV8GKR8WByfW8LC4aMxk6gj71 \
--bootnode /ip4/127.00.1/tcp/31330/p2p/QmSjcNmhbRvek3YDQAAQ3rV8GKR8WByfW8LC4aMxk6gj7v \
--client_peer_id QmbRz8Bt1pMcVnUzVQpL2icveZz2MF7VtELC44v8kVNwiG \
--delegate_reward_rate 0.125 \
--stake_to_be_added 100.00
```

#### Activate node
  - Call `activate_subnet_node` in Hypertensor on your start epoch up to the grace period.

##### Example Register & Stake CLI
```bash
activate-node --subnet_id 1
```
---
## Running Nodes

- Replace port `31330` with your port of choice.
- Replace `{your_ip}` with your IP.

### Run a Bootnode

A bootnode is an entry point into a decentralized network and should be ran on its own server.

Each subnet must have at least one public and running bootnode at all times for nodes to enter and for for Overwatch Nodes to validate a subnet. See documentation for more information.

<b>Note</b>: To be verified to have a proof-of-stake in-subnet, use the bootnode private key generated during the <b>Generate peer private keys</b> step that the subnet node was registered with under the `bootnode_peer_id`.

<b>Note</b>: Bootnodes are not required by subnet nodes and are expected to be managed by the subnet owner entity.

#### Start Bootnode

```bash
mesh-dht \
--host_maddrs /ip4/0.0.0.0/tcp/31330 /ip4/0.0.0.0/udp/31330/quic \
--announce_maddrs /ip4/{your_ip}/tcp/31330 /ip4/{your_ip}/udp/31330/quic \
--identity_path alith.id \
```
##### Update `PUBLIC_INITIAL_PEERS`

Once you run it, look at the outputs and find the following line:

```bash
Mon 00 01:23:45.678 [INFO] Running a DHT instance. To connect other peers to this one, use --initial_peers /ip4/YOUR_ADDRESS_HERE/tcp/31330/p2p/QmTPAIfThisIsMyAddressGoFindYoursnCfj
```

Once the bootnode is deployed, copy the `/ip4/YOUR_ADDRESS_HERE/tcp/31330/p2p/QmTPAIfThisIsMyAddressGoFindYoursnCfj` into the `PUBLIC_INITIAL_PEERS` in the `.env` file.

#### Start Node and Join Subnet
##### This joins an existing subnets and runs a bootnode.
- Get the bootnode multiaddresses from the subnets team or blockchain and add them to the `initial_peers` argument and replace `/ip4/{ip}/p2p/{peer_id}`. In this example, we use 2 bootnodes to connect to, but one is required.
```bash
mesh-dht \
--host_maddrs /ip4/0.0.0.0/tcp/31330 /ip4/0.0.0.0/udp/31330/quic \
--announce_maddrs /ip4/{your_ip} \
--initial_peers /ip4/{ip}/p2p/{peer_id} /ip4/{ip}/p2p/{peer_id}
```

### Node 
#### *Fill in how to start and run a node for your subnet!*

*The following is example only for deploying a subnet with no use-case.*

#### Start DHT / Start Node

This will start a new subnet (fresh swarm as initial node/bootnode and server in one). It is <b>not</b> required to run a node as a bootnode together. Bootnodes should be treated as contact point for entry only.

```bash
mesh-server-mock \
--host_maddrs /ip4/0.0.0.0/tcp/31330 /ip4/0.0.0.0/udp/31330/quic \
--announce_maddrs /ip4/{your_ip}/tcp/31330 /ip4/{your_ip}/udp/31330/quic \
--identity_path bootnode.id \
--new_swarm  \
--subnet_id 1 --subnet_node_id 1
```

##### Update `PUBLIC_INITIAL_PEERS`

Once you run it, look at the outputs and find the following line:

```bash
Mon 00 01:23:45.678 [INFO] Running a DHT instance. To connect other peers to this one, use --initial_peers /ip4/YOUR_ADDRESS_HERE/tcp/31330/p2p/QmTPAIfThisIsMyAddressGoFindYoursnCfj
```

Once the bootnode is deployed, copy the `/ip4/YOUR_ADDRESS_HERE/tcp/31330/p2p/QmTPAIfThisIsMyAddressGoFindYoursnCfj` into the `PUBLIC_INITIAL_PEERS` in the `.env` file.

#### Join DHT / Start Node
```bash
mesh-server-mock \
--host_maddrs /ip4/0.0.0.0/tcp/31331 /ip4/0.0.0.0/udp/31331/quic \
--announce_maddrs /ip4/{your_ip}/tcp/31331 /ip4/{your_ip}/udp/31331/quic \
--identity_path alith.id \
--subnet_id 1 --subnet_node_id 1
```
---

## Running Nodes Locally
Start a mesh locally with 3 nodes and no requirement for a blockchain connection:

#### Start the bootnode as a server 
This is a node that as a bootnode and a server, although this is not recommended for production.

<b>Note:</b> In production, a bootnode should <b>not</b> be ran as a server.

```bash
mesh-server-mock \
    --host_maddrs /ip4/0.0.0.0/tcp/31330 /ip4/0.0.0.0/udp/31330/quic \
    --announce_maddrs /ip4/{your_ip}/tcp/31330 /ip4/{your_ip}/udp/31330/quic \
    --identity_path bootnode.id \
    --subnet_id 1 --subnet_node_id 1 \
    --no_blockchain_rpc \
    --new_swarm
```
##### Update `PUBLIC_INITIAL_PEERS`

Once you run it, look at the outputs and find the following line:

```bash
Mon 00 01:23:45.678 [INFO] Running a DHT instance. To connect other peers to this one, use --initial_peers /ip4/YOUR_ADDRESS_HERE/tcp/31337/p2p/QmTPAIfThisIsMyAddressGoFindYoursnCfj
```

Once the bootnode is deployed, copy the `/ip4/YOUR_ADDRESS_HERE/tcp/31337/p2p/QmTPAIfThisIsMyAddressGoFindYoursnCfj` into the `PUBLIC_INITIAL_PEERS` in the `.env` file.

#### Start Node 2
```bash
mesh-server-mock \
    --host_maddrs /ip4/0.0.0.0/tcp/31331 /ip4/0.0.0.0/udp/31331/quic \
    --announce_maddrs /ip4/{your_ip}/tcp/31331 /ip4/{your_ip}/udp/31331/quic \
    --identity_path alith.id \
    --subnet_id 1 --subnet_node_id 2 \
    --no_blockchain_rpc
```

#### Start Node 3
```bash
mesh-server-mock \
    --host_maddrs /ip4/0.0.0.0/tcp/31332 /ip4/0.0.0.0/udp/31332/quic \
    --announce_maddrs /ip4/{your_ip}/tcp/31332 /ip4/{your_ip}/udp/31332/quic \
    --identity_path baltathar.id \
    --subnet_id 1 --subnet_node_id 3 \
    --no_blockchain_rpc
```

##### Add more nodes by using the following test `identity_path`'s:

- `charleth.id`
- `dorothy.id`
- `ethan.id`
- `faith.id`

<b>Note:</b> Ensure each peer has its own unique `subnet_node_id` and `port`.

---
## Running Nodes Locally With Local Blockchain

The following example will use Alith as the subnet owner and as the node example (registering and running the node). To add more nodes for testing with a running local blockchain, see `mesh/mesh_cli/hypertensor/README.md` to view each test identity path, it's hotkeys, coldkeys, and their peer IDs.

See `mesh/mesh_cli/hypertensor/node/register.py` to register more test accounts.

##### For testing with a running local blockchain
1. Register subnet
2. Register at least 3 nodes
3. Run the nodes
4. Activate the subnet

Once the subnet is activated, consensus will begin on the following epoch between all of the nodes in the subnet.

#### Register a subnet:
With Alith's coldkey as the owner and with Alith, Baltathar, Charleth, and Dorothy as the initial coldkeys:
```bash
register-subnet \
  --max_cost 100.00 \
  --name subnet-1 \
  --repo github.com/subnet-1 \
  --description "artificial intelligence" \
  --misc "cool subnet" \
  --churn_limit 64 \
  --min_stake 100.00 \
  --max_stake  1000.00 \
  --delegate_stake_percentage 0.1 \
  --subnet_node_queue_epochs 10 \
  --idle_classification_epochs 10 \
  --included_classification_epochs 10 \
  --max_node_penalties 10 \
  --initial_coldkeys "0xf24FF3a9CF04c71Dbc94D0b566f7A27B94566cac" "0x3Cd0A705a2DC65e5b1E1205896BaA2be8A07c6e0" "0x798d4Ba9baf0064Ec19eB4F0a1a45785ae9D6DFc" "0x773539d4Ac0e786233D90A233654ccEE26a613D9" \
  --max_registered_nodes 10 \
  --key_types "Rsa" \
  --bootnodes "test_bootnode" \
  --private_key "0x5fb92d6e98884f76de468fa3f6278f8807c48bebc13595d45af5bdc4da702133" \
  --local_rpc
```
#### Register a node:
<b>Note:</b> The client peer ID, bootnode peer ID, and bootnode are only for testing purposes. In production, the client peer ID and bootnode peer ID should be generated beforehand and each have its own identity paths (the bootnode will be derived from the bootnode peer ID if utilized). The client and bootnode peer ID are required on-chain but not required to be used off-chain in the subnet. The bootnode is optional.

Using Alith's coldkey private key:
```bash
register-node \
  --subnet_id 1 \
  --hotkey 0x317D7a5a2ba5787A99BE4693Eb340a10C71d680b \
  --peer_id QmShJYgxNoKn7xqdRQj5PBcNfPSsbWkgFBPA4mK5PH73JB \
  --bootnode_peer_id QmShJYgxNoKn7xqdRQj5PBcNfPSsbWkgFBPA4mK5PH73JC \
  --bootnode /ip4/127.00.1/tcp/31330/p2p/QmShJYgxNoKn7xqdRQj5PBcNfPSsbWkgFBPA4mK5PH73JC \
  --client_peer_id QmShJYgxNoKn7xqdRQj5PBcNfPSsbWkgFBPA4mK5PH73JD \
  --delegate_reward_rate 0.125 \
  --stake_to_be_added 100.00 \
  --max_burn_amount 100.00 \
  --private_key "0x5fb92d6e98884f76de468fa3f6278f8807c48bebc13595d45af5bdc4da702133" \
  --local_rpc
```
Get the subnet node ID after registration

#### Run a node
Using Alith's hotkey private key:
```bash
mesh-server-mock \
    --host_maddrs /ip4/0.0.0.0/tcp/31331 /ip4/0.0.0.0/udp/31331/quic \
    --announce_maddrs /ip4/{your_ip}/tcp/31331 /ip4/{your_ip}/udp/31331/quic \
    --identity_path alith.id \
    --subnet_id 1 --subnet_node_id 2 \
    --local_rpc \
    --private_key "0x51b7c50c1cd27de89a361210431e8f03a7ddda1a0c8c5ff4e4658ca81ac02720"
```

## Future

- Migrate to py-libp2p (from go-libp2p-daemon).
- Random-walk
- Gossip protocol integration
- Noise Protocol (Diffie-Hellman key exchange)
- Onion routing or mixnet options
- Multiple encryption options
- Explore alternative tensor/AI parameter compression options
- DHT Record uniqueness options
- Runtime upgrades
- In-subnet epochs (synced to blockchain clock) standard with ledger
- Ledger integration
- Runtime upgrade
  - Versioned protocols
  - Orchestration tooling
  - Blue-green deployment standardizations
- Etc.
---

## Contributing

This is currently at the active development stage, and we welcome all contributions. Everything, from bug fixes and documentation improvements to entirely new features, is appreciated.

If you want to contribute to this mesh template but don't know where to start, take a look at the unresolved [issues](https://github.com/hypertensor-blockchain/mesh/issues). 

Open a new issue or join [our chat room](https://discord.gg/bY7NUEweQp) in case you want to discuss new functionality or report a possible bug. Bug fixes are always welcome, but new features should be preferably discussed with maintainers beforehand.


[![Discord](https://img.shields.io/badge/Join-Discord-blue?logo=discord&logoColor=white)](https://discord.gg/bY7NUEweQp)
[![X](https://img.shields.io/badge/Follow-On_X-black?logo=x&logoColor=white)](https://x.com/hyper_tensor)
[![Telegram](https://img.shields.io/badge/Join-Telegram-blue?logo=telegram&logoColor=white)](https://t.me/hypertensorblockchain)

## References

[0]: Maymounkov, P., & Mazières, D. (2002). Kademlia: A Peer-to-Peer Information System Based on the XOR Metric. In P. Druschel, F. Kaashoek, & A. Rowstron (Eds.), Peer-to-Peer Systems (pp. 53–65). Berlin, Heidelberg: Springer Berlin Heidelberg. https://doi.org/10.1007/3-540-45748-8_5

[1]: Baumgart, I., & Mies, S. (2014). S / Kademlia : A practicable approach towards secure key-based routing S / Kademlia : A Practicable Approach Towards Secure Key-Based Routing, (June). https://doi.org/10.1109/ICPADS.2007.4447808

[2]: Freedman, M. J., & Mazières, D. (2003). Sloppy Hashing and Self-Organizing Clusters. In IPTPS. Springer Berlin / Heidelberg. Retrieved from https://www.cs.princeton.edu/~mfreed/docs/coral-iptps03.pdf

[bittorrent]: http://bittorrent.org/beps/bep_0005.html

[uvarint-spec]: https://github.com/multiformats/unsigned-varint

[ping]: https://github.com/libp2p/specs/issues/183

[go-libp2p-xor]: https://github.com/libp2p/go-libp2p-xor

[provider-record-measurements]: https://github.com/protocol/network-measurements/blob/master/results/rfm17-provider-record-liveness.md