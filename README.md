## A decentralized subnet base for Hypertensor.

The Hypertensor Subnet Base includes all the core components required to launch a decentralized AI application, including:
- **[Kademlia DHT (KAD-DHT)][bittorrent]** – for scalable, decentralized storage and routing
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

# Subnet Documentation

##### Generate coldkey (if needed)

##### Generate hotkey
- This is the hotkey of the node. It is used for validating and attesting only. Each hotkey is unique to each subnet node and no hotkey can be used twice.

##### Generate peer private keys

  - This will create 3 private key files for your peer
      - `peer_id`: Main peer ID for communication and signing
      - `bootstrap_peer_id`: (Optional usage) Peer ID to be used as a bootstrap node.
      - `client_peer_id`: (Optional usage) Peer ID to be used as a client. This is for those who want to build frontends to interact with the subnet.

##### Register & Stake on Hypertensor
  - Call `register_subnet_node`
  - Retrieve your `start_epoch` by querying your SubnetNodesData storage element on polkadot.js with your subnet node ID. This is the epoch you must activate your node on + the grace period

##### Run subnet node
<i>(fill in docs here, examples are alow below)</i>

##### Activate node
  - Call `activate_subnet_node` in Hypertensor on your start epoch up to the grace period.

---
## Running Nodes
Fill in the following with your subnets documentation on how to join the subnet, requirements, etc.

### Run bootnode 
A bootnode is an entry point into a decentralized network. 

Each subnet must have at least one public and running bootnode at all times available for Overwatch Nodes to validate a subnet is running.

- Replace port 31330 with your port of choice.
- Replace `{your_ip}` with your IP.

##### Start Bootnode and Start Subnet
###### This starts an entirely new subnet and runs a bootnode
```bash
mesh-dht \
--host_maddrs /ip4/0.0.0.0/tcp/31330 /ip4/0.0.0.0/udp/31330/quic \
--announce_maddrs /ip4/{your_ip}/tcp/31330 /ip4/{your_ip}/udp/31330/quic \
--identity_path server2.id
```

##### Start Bootnode and Join Subnet
###### This joins an existing subnets and runs a bootnode.
- Get the bootnode multiaddresses from the subnets team or blockchain and add them to the `initial_peers` argument.
```bash
mesh-dht \
--host_maddrs /ip4/0.0.0.0/tcp/31330 /ip4/0.0.0.0/udp/31330/quic \
--announce_maddrs /ip4/{your_ip} \
--initial_peers /ip4/{ip}/p2p/{peer_id} /ip4/{ip}/p2p/{peer_id}
```

### Run node 
*Fill in how to start and run a node for your subnet!*

##### Start DHT / Start Node
NOT SUGGESTED
This will start a new subnet (fresh swarm as initial node)
```bash
mesh-server-mock \
--host_maddrs /ip4/0.0.0.0/tcp/31330 /ip4/0.0.0.0/udp/31330/quic \
--announce_maddrs /ip4/{your_ip}/tcp/31330 /ip4/{your_ip}/udp/31330/quic \
--identity_path server2.id \
--new_swarm  \
--subnet_id 1 --subnet_node_id 1
```

##### Join DHT / Start Node
```bash
mesh-server-mock \
--host_maddrs /ip4/0.0.0.0/tcp/31330 /ip4/0.0.0.0/udp/31330/quic \
--announce_maddrs /ip4/{your_ip}/tcp/31330 /ip4/{your_ip}/udp/31330/quic \
--identity_path server2.id \
--subnet_id 1 --subnet_node_id 1
```

---

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
- In-subnet epochs (synced to blockchain clock), plus ledger integration
- Etc.
---

## Contributing

This is currently at the active development stage, and we welcome all contributions. Everything, from bug fixes and documentation improvements to entirely new features, is appreciated.

If you want to contribute to this mesh template but don't know where to start, take a look at the unresolved [issues](https://github.com/hypertensor-blockchain/mesh/issues). 

Open a new issue or join [our chat room](https://discord.gg/bY7NUEweQp) in case you want to discuss new functionality or report a possible bug. Bug fixes are always welcome, but new features should be preferably discussed with maintainers beforehand.

## References

[0]: Maymounkov, P., & Mazières, D. (2002). Kademlia: A Peer-to-Peer Information System Based on the XOR Metric. In P. Druschel, F. Kaashoek, & A. Rowstron (Eds.), Peer-to-Peer Systems (pp. 53–65). Berlin, Heidelberg: Springer Berlin Heidelberg. https://doi.org/10.1007/3-540-45748-8_5

[1]: Baumgart, I., & Mies, S. (2014). S / Kademlia : A practicable approach towards secure key-based routing S / Kademlia : A Practicable Approach Towards Secure Key-Based Routing, (June). https://doi.org/10.1109/ICPADS.2007.4447808

[2]: Freedman, M. J., & Mazières, D. (2003). Sloppy Hashing and Self-Organizing Clusters. In IPTPS. Springer Berlin / Heidelberg. Retrieved from https://www.cs.princeton.edu/~mfreed/docs/coral-iptps03.pdf

[bittorrent]: http://bittorrent.org/beps/bep_0005.html

[uvarint-spec]: https://github.com/multiformats/unsigned-varint

[ping]: https://github.com/libp2p/specs/issues/183

[go-libp2p-xor]: https://github.com/libp2p/go-libp2p-xor

[provider-record-measurements]: https://github.com/protocol/network-measurements/blob/master/results/rfm17-provider-record-liveness.md