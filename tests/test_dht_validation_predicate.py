import asyncio
import io
import os
import random
import time
from typing import List

import pytest
import torch

import mesh
from mesh import get_dht_time
from mesh.dht.crypto import RSASignatureValidator
from mesh.dht.validation import HypertensorPredicateValidator, RecordValidatorBase
from mesh.subnet.utils.consensus import MAX_CONSENSUS_TIME, get_consensus_key
from mesh.subnet.utils.key import generate_rsa_private_key_file, get_rsa_peer_id, get_rsa_private_key
from mesh.substrate.config import BLOCK_SECS

from test_utils.dht_swarms import launch_dht_instances_with_record_validators2
from test_utils.hypertensor_predicate import (
    hypertensor_consensus_predicate,
)
from test_utils.mock_hypertensor_json import MockHypertensor, write_epoch_json

# pytest tests/test_dht_validation_predicate.py -rP

# pytest tests/test_dht_validation_predicate.py::test_consensus_with_key_validator -rP

@pytest.mark.forked
@pytest.mark.asyncio
async def test_consensus_with_key_validator():
    predicate = hypertensor_consensus_predicate()
    hypertensor = MockHypertensor()
    # start at commit phase 0%

    block_per_epoch = 100
    seconds_per_epoch = BLOCK_SECS * block_per_epoch
    current_block = 100
    epoch_length = 100
    epoch = current_block // epoch_length
    blocks_elapsed = current_block % epoch_length
    percent_complete = blocks_elapsed / epoch_length
    blocks_remaining = epoch_length - blocks_elapsed
    seconds_elapsed = blocks_elapsed * BLOCK_SECS
    seconds_remaining = blocks_remaining * BLOCK_SECS

    write_epoch_json({
        "block": current_block,
        "epoch": epoch,
        "block_per_epoch": block_per_epoch,
        "seconds_per_epoch": seconds_per_epoch,
        "percent_complete": percent_complete,
        "blocks_elapsed": blocks_elapsed,
        "blocks_remaining": blocks_remaining,
        "seconds_elapsed": seconds_elapsed,
        "seconds_remaining": seconds_remaining
    })

    time.sleep(5)

    peers_len = 10
    test_paths = []
    record_validators: List[List[RecordValidatorBase]] = []
    for i in range(peers_len):
        test_path = f"rsa_test_path_{i}.key"
        test_paths.append(test_path)
        private_key, public_key, public_bytes, encoded_public_key, encoded_digest, peer_id = generate_rsa_private_key_file(test_path)
        loaded_key = get_rsa_private_key(test_path)
        record_validator = RSASignatureValidator(loaded_key)
        consensus_predicate = HypertensorPredicateValidator(
            hypertensor=hypertensor,
            record_predicate=predicate,
        )
        record_validators.append([record_validator, consensus_predicate])
        peer_id = get_rsa_peer_id(public_bytes)

    dhts = launch_dht_instances_with_record_validators2(
        record_validators=record_validators,
        identity_paths=test_paths
    )

    used_dhts = []
    used_dhts.append(dhts[0])

    _max_consensus_time = MAX_CONSENSUS_TIME - 60

    consensus_key = get_consensus_key(epoch)
    tensor = torch.randn(2, 2)
    buffer = io.BytesIO()
    torch.save(tensor, buffer)
    buffer.seek(0)
    value = buffer.read()

    store_ok = dhts[0].store(consensus_key, value, get_dht_time() + _max_consensus_time, subkey=record_validators[0][0].local_public_key)
    assert store_ok is True

    other_dhts = [dht for dht in dhts if dht not in used_dhts]
    assert other_dhts, "No other DHTs available. "

    someone = random.choice(other_dhts)
    used_dhts.append(someone)

    results = someone.get(consensus_key)
    assert results is not None
    payload = next(iter(results.value.values())).value
    assert payload == value, "Incorrect value in payload. "

    time.sleep(5)

    block_per_epoch = 100
    seconds_per_epoch = BLOCK_SECS * block_per_epoch
    current_block = 190
    epoch_length = 100
    epoch = current_block // epoch_length
    blocks_elapsed = current_block % epoch_length
    percent_complete = blocks_elapsed / epoch_length
    blocks_remaining = epoch_length - blocks_elapsed
    seconds_elapsed = blocks_elapsed * BLOCK_SECS
    seconds_remaining = blocks_remaining * BLOCK_SECS

    write_epoch_json({
        "block": current_block,
        "epoch": epoch,
        "block_per_epoch": block_per_epoch,
        "seconds_per_epoch": seconds_per_epoch,
        "percent_complete": percent_complete,
        "blocks_elapsed": blocks_elapsed,
        "blocks_remaining": blocks_remaining,
        "seconds_elapsed": seconds_elapsed,
        "seconds_remaining": seconds_remaining
    })

    other_dhts = [dht for dht in dhts if dht not in used_dhts]
    assert other_dhts, "No other DHTs available. "

    someone_new = random.choice(other_dhts)
    used_dhts.append(someone)

    epoch_progress = hypertensor.get_epoch_progress()
    print("epoch_progress", epoch_progress)

    results = someone_new.get(consensus_key)
    print("results", results)
    assert results is not None

    for dht in dhts:
        dht.shutdown()

    for path in test_paths:
        os.remove(path)
