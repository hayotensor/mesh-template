
# Local Mock Hypertensor

## Overview

This is a simulated blockchain environment for local testing. It is an sqlite database to simulate extrinsics and RPC methods.

## Usage

### When starting a bootnode

If no initial peers are specified in the arguments via `--initial_peers` it will delete the database and reinitialize a new one. Otherwise, it will not remove the database.

### When starting a node

If a new swarm is specified in the arguments via `--new_swarm` (using `--new_swarm` creates a new fresh swarm of peers, this node can be used as the bootnode. In production, subnets should rely on bootnodes for connection and not validator nodes) it will delete the database and reinitialize a new one. Otherwise, it will not remove the database.

**Ensure** when starting nodes, they all use **unique** `--subnet_node_id` arguments.

### Contributing

File a new issue on [GitHub](https://github.com/hypertensor-blockchain/subnet-template/issues)