


import pytest
import scalecodec
from scalecodec.base import RuntimeConfiguration, ScaleBytes
from scalecodec.type_registry import load_type_registry_preset
from scalecodec.utils.ss58 import ss58_encode

from mesh.substrate.chain_data import ConsensusData, SubnetInfo
from mesh.substrate.chain_functions import Hypertensor, KeypairFrom, SubnetNodeClass

custom_types = {
  "types": {
    "SubnetData": {
      "type": "struct",
      "type_mapping": [
        ["id", "u32"],
        ["name", "Vec<u8>"],
        ["repo", "Vec<u8>"],
        ["description", "Vec<u8>"],
        ["misc", "Vec<u8>"],
        ["state", "SubnetState"],
        ["start_epoch", "u32"],
      ],
    },
    "SubnetInfo": {
      "type": "struct",
      "type_mapping": [
        ["id", "u32"],
        ["name", "Vec<u8>"],
        ["repo", "Vec<u8>"],
        ["description", "Vec<u8>"],
        ["misc", "Vec<u8>"],
        ["state", "SubnetState"],
        ["start_epoch", "u32"],
        ["churn_limit", "u32"],
        ["min_stake", "u128"],
        ["max_stake", "u128"],
        ["delegate_stake_percentage", "u128"],
        ["registration_queue_epochs", "u32"],
        ["activation_grace_epochs", "u32"],
        ["queue_classification_epochs", "u32"],
        ["included_classification_epochs", "u32"],
        ["max_node_penalties", "u32"],
        ["initial_coldkeys", "Option<Vec<[u8; 20]>>"],
        ["max_registered_nodes", "u32"],
        ["owner", "Option<[u8; 20]>"],
        ["registration_epoch", "Option<u32>"],
        ["key_types", "Vec<KeyType>"],
        ["slot_index", "Option<u32>"],
        ["penalty_count", "u32"],
        ["total_nodes", "u32"],
        ["total_active_nodes", "u32"],
        ["total_electable_nodes", "u32"],
      ],
    },
    "SubnetState": {
      "type": "enum",
      "value_list": [
        "Registered",
        "Active",
        "Paused",
      ],
    },
    # "NodeRemovalPolicy": {
    #   "type": "struct",
    #   "type_mapping": [
    #     ["logic", "LogicExpr"],
    #   ],
    # },
    # "LogicExpr": {
    #   "type": "enum",
    #   "value_list": [
    #     "And(Box<LogicExpr>, Box<LogicExpr>)",
    #     "Or(Box<LogicExpr>, Box<LogicExpr>)",
    #     "Xor(Box<LogicExpr>, Box<LogicExpr>)",
    #     "Not(Box<LogicExpr>)",
    #     "Condition(NodeRemovalConditionType)"
    #   ],
    # },
    # "NodeRemovalConditionType": {
    #   "type": "enum",
    #   "value_list": [
    #     "HardBelowScore(u128)",
    #     "HardBelowAverageAttestation(u128)",
    #     "HardBelowNodeDelegateStakeRate(u128)",
    #     "DeltaBelowScore(u128)",
    #     "DeltaBelowAverageAttestation(u128)",
    #     "DeltaBelowNodeDelegateStakeRate(u128)",
    #     "DeltaBelowNodeDelegateStakeBalance(u128)",
    #     "DeltaBelowStakeBalance(u128)",
    #   ],
    # },
    "KeyType": {
      "type": "enum",
      "value_list": [
        "Rsa",
        "Ed25519",
        "Secp256k1",
        "Ecdsa",
      ],
    },
    "SubnetNode": {
      "type": "struct",
      "type_mapping": [
        ["id", "u32"],
        ["hotkey", "[u8; 20]"],
        ["peer_id", "OpaquePeerId"],
        ["bootnode_peer_id", "OpaquePeerId"],
        ["bootnode", "Option<BoundedVec<u8, DefaultMaxVectorLength>>"],
        ["client_peer_id", "OpaquePeerId"],
        ["classification", "SubnetNodeClassification"],
        ["delegate_reward_rate", "u128"],
        ["last_delegate_reward_rate_update", "u32"],
        ["unique", "Option<BoundedVec<u8, DefaultMaxVectorLength>>"],
        ["non_unique", "Option<BoundedVec<u8, DefaultMaxVectorLength>>"],
      ],
    },
    "SubnetNodeClassification": {
      "type": "struct",
      "type_mapping": [
        ["node_class", "SubnetNodeClass"],
        ["start_epoch", "u32"],
      ],
    },
    "SubnetNodeClass": {
      "type": "enum",
      "value_list": [
        "Deactivated",
        "Registered",
        "Idle",
        "Included",
        "Validator",
      ],
    },
    "SubnetNodeConsensusData": {
      "type": "struct",
      "type_mapping": [
        ["subnet_node_id", "u32"],
        ["score", "u128"],
      ],
    },
    "RewardsData": {
      "type": "struct",
      "type_mapping": [
        ["overall_subnet_reward", "u128"],
        ["subnet_owner_reward", "u128"],
        ["subnet_rewards", "u128"],
        ["delegate_stake_rewards", "u128"],
        ["subnet_node_rewards", "u128"],
      ],
    },
    "SubnetNodeInfo": {
      "type": "struct",
      "type_mapping": [
        ["subnet_node_id", "u32"],
        ["coldkey", "[u8; 20]"],
        ["hotkey", "[u8; 20]"],
        ["peer_id", "Vec<u8>"],
        ["bootnode_peer_id", "Vec<u8>"],
        ["client_peer_id", "Vec<u8>"],
        ["bootnode", "Vec<u8>"],
        ["identity", "ColdkeyIdentityData"],
        ["classification", "SubnetNodeClassification"],
        ["delegate_reward_rate", "u128"],
        ["last_delegate_reward_rate_update", "u32"],
        ["unique", "Option<BoundedVec<u8, DefaultMaxVectorLength>>"],
        ["non_unique", "Option<BoundedVec<u8, DefaultMaxVectorLength>>"],
        ["stake_balance", "u128"],
        ["node_delegate_stake_balance", "u128"],
        ["penalties", "u32"],
        ["reputation", "Reputation"],
      ],
    },
    "Reputation": {
      "type": "struct",
      "type_mapping": [
        ["start_epoch", "u32"],
        ["score", "u128"],
        ["lifetime_node_count", "u32"],
        ["total_active_nodes", "u32"],
        ["total_increases", "u32"],
        ["total_decreases", "u32"],
        ["average_attestation", "u128"],
        ["last_validator_epoch", "u32"],
        ["ow_score", "u32"],
      ],
    },
    "ColdkeyIdentityData": {
      "type": "struct",
      "type_mapping": [
        ["name", "BoundedVec<u8, DefaultMaxVectorLength>"],
        ["url", "BoundedVec<u8, DefaultMaxUrlLength>"],
        ["image", "BoundedVec<u8, DefaultMaxUrlLength>"],
        ["discord", "BoundedVec<u8, DefaultMaxSocialIdLength>"],
        ["x", "BoundedVec<u8, DefaultMaxSocialIdLength>"],
        ["telegram", "BoundedVec<u8, DefaultMaxSocialIdLength>"],
        ["github", "BoundedVec<u8, DefaultMaxUrlLength>"],
        ["hugging_face", "BoundedVec<u8, DefaultMaxUrlLength>"],
        ["description", "BoundedVec<u8, DefaultMaxVectorLength>"],
        ["misc", "BoundedVec<u8, DefaultMaxVectorLength>"],
      ],
    },
    "AttestEntry": {
      "type": "struct",
      "type_mapping": [
        ["block", "u32"],
        ["data", "Option<BoundedVec<u8, DefaultValidatorArgsLimit>>"]
      ]
    },
    "ConsensusData": {
      "type": "struct",
      "type_mapping": [
        ["validator_id", "u32"],
        ["attests", "BTreeMap<u32, AttestEntry>"],
        ["subnet_nodes", "Vec<SubnetNode<AccountId>>"],
        ["data", "Vec<SubnetNodeConsensusData>"],
        ["args", "Option<BoundedVec<u8, DefaultValidatorArgsLimit>>"],
      ],
    },
    "ConsensusSubmissionData": {
      "type": "struct",
      "type_mapping": [
        ["validator_subnet_node_id", "u32"],
        ["attestation_ratio", "u128"],
        ["weight_sum", "u128"],
        ["data_length", "u32"],
        ["data", "Vec<SubnetNodeConsensusData>"],
        ["subnet_nodes", "Vec<SubnetNode<[u8; 20]>>"],
      ],
    },
    "BoundedVec<u8, DefaultMaxVectorLength>": "Vec<u8>",
    "BoundedVec<u8, DefaultMaxUrlLength>": "Vec<u8>",
    "BoundedVec<u8, DefaultMaxSocialIdLength>": "Vec<u8>",
    "BoundedVec<u8, DefaultValidatorArgsLimit>": "Vec<u8>",
    "Option<BoundedVec<u8, DefaultMaxVectorLength>>": "Option<Vec<u8>>",
    "Option<BoundedVec<u8, DefaultMaxUrlLength>>": "Option<Vec<u8>>",
    "Option<BoundedVec<u8, DefaultMaxSocialIdLength>>": "Option<Vec<u8>>",
    "Option<BoundedVec<u8, DefaultValidatorArgsLimit>>": "Option<Vec<u8>>",
  }
}


# custom_types = {
#     "types": {
#         "SubnetNodeTest": {
#             "type": "struct",
#             "type_mapping": [
#                 ["id", "u32"],
#                 ["hotkey", "[u8; 20]"],
#                 ["peer_id", "OpaquePeerId"],
#                 ["bootnode_peer_id", "OpaquePeerId"],
#             ]
#         },
#     }
# }


LOCAL_RPC="ws://127.0.0.1:9944"

# pytest tests/substrate/test_rpc.py -rP

hypertensor = Hypertensor(LOCAL_RPC, "0x5fb92d6e98884f76de468fa3f6278f8807c48bebc13595d45af5bdc4da702133", KeypairFrom.PRIVATE_KEY)

# pytest tests/substrate/test_rpc.py::test_get_subnet_info -rP

def test_get_subnet_info():
    rpc_runtime_config = RuntimeConfiguration()
    rpc_runtime_config.update_type_registry(load_type_registry_preset("legacy"))
    rpc_runtime_config.update_type_registry(custom_types)

    with hypertensor.interface as _interface:
        result = _interface.rpc_request(
            method='network_getSubnetInfo',
            params=[1]
        )
        print("Raw result:", result)
        scale_obj = rpc_runtime_config.create_scale_object("Option<SubnetInfo>")
        type_info = scale_obj.generate_type_decomposition()
        print("type_info", type_info)

        if 'result' in result and result['result']:
            try:
                # Create scale object for decoding
                obj = rpc_runtime_config.create_scale_object('Option<SubnetInfo>')

                # Decode the hex-encoded SCALE data (don't encode!)
                decoded_data = obj.decode(ScaleBytes(bytes(result['result'])))
                print("Decoded data:", decoded_data)

            except Exception as e:
                print("Decode error:", str(e))

            try:
                # Create scale object for decoding
                obj = rpc_runtime_config.create_scale_object('Option<SubnetInfo>', data=ScaleBytes(bytes(result['result'])))

                # Decode the hex-encoded SCALE data (don't encode!)
                decoded_data = obj.decode()
                print("Decoded data:", decoded_data)

            except Exception as e:
                print("Decode error:", str(e))

# pytest tests/substrate/test_rpc.py::test_get_subnet_info_formatted -rP

def test_get_subnet_info_formatted():
    subnet_info = hypertensor.get_formatted_subnet_info(1)
    print("subnet_info", subnet_info)
    assert subnet_info is not None

# pytest tests/substrate/test_rpc.py::test_get_subnet_node_info -rP

def test_get_subnet_node_info():
    rpc_runtime_config = RuntimeConfiguration()
    rpc_runtime_config.update_type_registry(load_type_registry_preset("legacy"))
    rpc_runtime_config.update_type_registry(custom_types)

    print("SubnetNodeClass", SubnetNodeClass.Idle.value)

    with hypertensor.interface as _interface:
        result = _interface.rpc_request(
            method='network_getMinClassSubnetNodes',
            params=[1, 0, SubnetNodeClass.Idle.value]
        )
        print("Raw result:", result)
        scale_obj = rpc_runtime_config.create_scale_object("Vec<SubnetNode>")
        type_info = scale_obj.generate_type_decomposition()
        print("type_info", type_info)

        if 'result' in result and result['result']:
            try:
                # Create scale object for decoding
                obj = rpc_runtime_config.create_scale_object('Vec<SubnetNode>')

                # Decode the hex-encoded SCALE data (don't encode!)
                decoded_data = obj.decode(ScaleBytes(bytes(result['result'])))
                print("Decoded data:", decoded_data)

            except Exception as e:
                print("Decode error:", str(e))

            try:
                # Create scale object for decoding
                obj = rpc_runtime_config.create_scale_object('Vec<SubnetNode>', data=ScaleBytes(bytes(result['result'])))

                # Decode the hex-encoded SCALE data (don't encode!)
                decoded_data = obj.decode()
                print("Decoded data:", decoded_data)

            except Exception as e:
                print("Decode error:", str(e))

# pytest tests/substrate/test_rpc.py::test_get_subnet_node_info_hypertensor -rP

def test_get_subnet_node_info_hypertensor():
    nodes = hypertensor.get_min_class_subnet_nodes_formatted(1, 0, SubnetNodeClass.Idle)
    print("nodes", nodes)

# pytest tests/substrate/test_rpc.py::test_get_subnet_data -rP

def test_get_subnet_data():
    rpc_runtime_config = RuntimeConfiguration()
    rpc_runtime_config.update_type_registry(load_type_registry_preset("legacy"))
    rpc_runtime_config.update_type_registry(custom_types)

    with hypertensor.interface as _interface:
        result = _interface.rpc_request(
            method='network_getSubnetData',
            params=[1]
        )
        print("Raw result:", result)
        if 'result' in result and result['result']:
            try:
                # Create scale object for decoding
                obj = rpc_runtime_config.create_scale_object('Option<SubnetData>')

                # Decode the hex-encoded SCALE data (don't encode!)
                decoded_data = obj.decode(ScaleBytes(bytes(result['result'])))
                print("Decoded data:", decoded_data)

            except Exception as e:
                print("Decode error:", str(e))

            try:
                # Create scale object for decoding
                obj = rpc_runtime_config.create_scale_object('Option<SubnetData>', data=ScaleBytes(bytes(result['result'])))

                # Decode the hex-encoded SCALE data (don't encode!)
                decoded_data = obj.decode()
                print("Decoded data:", decoded_data)

            except Exception as e:
                print("Decode error:", str(e))

consensus_result = [1, 3, 0, 0, 0, 4, 3, 0, 0, 0, 84, 0, 0, 0, 0, 12, 1, 0, 0, 0, 49, 125, 122, 90, 43, 165, 120, 122, 153, 190, 70, 147, 235, 52, 10, 16, 199, 29, 104, 11, 184, 81, 109, 83, 104, 74, 89, 103, 120, 78, 111, 75, 110, 55, 120, 113, 100, 82, 81, 106, 53, 80, 66, 99, 78, 102, 80, 83, 115, 98, 87, 107, 103, 70, 66, 80, 65, 52, 109, 75, 53, 80, 72, 55, 51, 74, 66, 184, 81, 109, 83, 104, 74, 89, 103, 120, 78, 111, 75, 110, 55, 120, 113, 100, 82, 81, 106, 53, 80, 66, 99, 78, 102, 80, 83, 115, 98, 87, 107, 103, 70, 66, 80, 65, 52, 109, 75, 53, 80, 72, 55, 51, 74, 67, 1, 41, 1, 47, 105, 112, 52, 47, 49, 50, 55, 46, 48, 48, 46, 49, 47, 116, 99, 112, 47, 51, 49, 51, 51, 48, 47, 112, 50, 112, 47, 81, 109, 83, 104, 74, 89, 103, 120, 78, 111, 75, 110, 55, 120, 113, 100, 82, 81, 106, 53, 80, 66, 99, 78, 102, 80, 83, 115, 98, 87, 107, 103, 70, 66, 80, 65, 52, 109, 75, 53, 80, 72, 55, 51, 74, 66, 184, 81, 109, 83, 104, 74, 89, 103, 120, 78, 111, 75, 110, 55, 120, 113, 100, 82, 81, 106, 53, 80, 66, 99, 78, 102, 80, 83, 115, 98, 87, 107, 103, 70, 66, 80, 65, 52, 109, 75, 53, 80, 72, 55, 51, 74, 68, 4, 0, 0, 0, 0, 0, 128, 236, 116, 214, 22, 188, 1, 0, 0, 0, 0, 0, 0, 0, 0, 8, 0, 0, 0, 0, 0, 2, 0, 0, 0, 195, 15, 233, 29, 233, 26, 63, 167, 158, 66, 223, 231, 160, 25, 23, 208, 217, 45, 153, 215, 184, 81, 109, 98, 82, 122, 56, 66, 116, 49, 112, 77, 99, 86, 110, 85, 122, 86, 81, 112, 76, 50, 105, 99, 118, 101, 90, 122, 50, 77, 70, 55, 86, 116, 69, 76, 67, 52, 52, 118, 56, 107, 86, 78, 119, 105, 71, 184, 81, 109, 98, 82, 122, 56, 66, 116, 49, 112, 77, 99, 86, 110, 85, 122, 86, 81, 112, 76, 50, 105, 99, 118, 101, 90, 122, 50, 77, 70, 55, 86, 116, 69, 76, 67, 52, 52, 118, 56, 107, 86, 78, 119, 105, 72, 1, 41, 1, 47, 105, 112, 52, 47, 49, 50, 55, 46, 48, 48, 46, 49, 47, 116, 99, 112, 47, 51, 49, 51, 51, 48, 47, 112, 50, 112, 47, 81, 109, 98, 82, 122, 56, 66, 116, 49, 112, 77, 99, 86, 110, 85, 122, 86, 81, 112, 76, 50, 105, 99, 118, 101, 90, 122, 50, 77, 70, 55, 86, 116, 69, 76, 67, 52, 52, 118, 56, 107, 86, 78, 119, 105, 71, 184, 81, 109, 98, 82, 122, 56, 66, 116, 49, 112, 77, 99, 86, 110, 85, 122, 86, 81, 112, 76, 50, 105, 99, 118, 101, 90, 122, 50, 77, 70, 55, 86, 116, 69, 76, 67, 52, 52, 118, 56, 107, 86, 78, 119, 105, 73, 4, 0, 0, 0, 0, 0, 128, 236, 116, 214, 22, 188, 1, 0, 0, 0, 0, 0, 0, 0, 0, 9, 0, 0, 0, 0, 0, 3, 0, 0, 0, 47, 119, 3, 186, 153, 83, 212, 34, 41, 64, 121, 161, 203, 50, 245, 210, 182, 14, 56, 235, 184, 81, 109, 84, 74, 56, 117, 121, 76, 74, 66, 119, 86, 112, 114, 101, 106, 85, 81, 102, 89, 70, 65, 121, 119, 100, 88, 87, 102, 100, 110, 85, 81, 98, 67, 49, 88, 105, 102, 54, 81, 105, 84, 78, 116, 97, 57, 184, 81, 109, 84, 74, 56, 117, 121, 76, 74, 66, 119, 86, 112, 114, 101, 106, 85, 81, 102, 89, 70, 65, 121, 119, 100, 88, 87, 102, 100, 110, 85, 81, 98, 67, 49, 88, 105, 102, 54, 81, 105, 84, 78, 116, 97, 48, 1, 41, 1, 47, 105, 112, 52, 47, 49, 50, 55, 46, 48, 48, 46, 49, 47, 116, 99, 112, 47, 51, 49, 51, 51, 48, 47, 112, 50, 112, 47, 81, 109, 84, 74, 56, 117, 121, 76, 74, 66, 119, 86, 112, 114, 101, 106, 85, 81, 102, 89, 70, 65, 121, 119, 100, 88, 87, 102, 100, 110, 85, 81, 98, 67, 49, 88, 105, 102, 54, 81, 105, 84, 78, 116, 97, 57, 188, 81, 109, 84, 74, 56, 117, 121, 76, 74, 66, 119, 86, 112, 114, 101, 106, 85, 81, 102, 89, 70, 65, 121, 119, 100, 88, 87, 102, 100, 110, 85, 81, 98, 67, 49, 88, 105, 102, 54, 81, 105, 84, 78, 116, 97, 57, 49, 4, 0, 0, 0, 0, 0, 128, 236, 116, 214, 22, 188, 1, 0, 0, 0, 0, 0, 0, 0, 0, 10, 0, 0, 0, 0, 0, 12, 1, 0, 0, 0, 0, 0, 100, 167, 179, 182, 224, 13, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 100, 167, 179, 182, 224, 13, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 100, 167, 179, 182, 224, 13, 0, 0, 0, 0, 0, 0, 0, 0, 0]

# pytest tests/substrate/test_rpc.py::test_get_consensus_data -rP

def test_get_consensus_data():
    consensus_data = ConsensusData.from_vec_u8(consensus_result)
    print("consensus_data: ", consensus_data)

    # attestation ratio
    attestation_ratio = len(consensus_data.attests) / len(consensus_data.subnet_nodes)
    print("attestation_ratio: ", attestation_ratio)

    # rpc_runtime_config = RuntimeConfiguration()
    # rpc_runtime_config.update_type_registry(load_type_registry_preset("legacy"))
    # rpc_runtime_config.update_type_registry(custom_types)

    # with hypertensor.interface as _interface:
    #   result = _interface.rpc_request(
    #     method='network_getConsensusData',
    #     params=[
    #       1,
    #       4
    #     ]
    #   )
    #   # print("Raw result:", result)
    #   if 'result' in result and result['result']:
    #       try:
    #           # Create scale object for decoding
    #           obj = rpc_runtime_config.create_scale_object('Option<ConsensusData>')

    #           # Decode the hex-encoded SCALE data (don't encode!)
    #           decoded_data = obj.decode(ScaleBytes(bytes(result['result'])))
    #           print("Decoded data:", decoded_data)

    #       except Exception as e:
    #           print("Decode error:", str(e))

    #       try:
    #           # Create scale object for decoding
    #           obj = rpc_runtime_config.create_scale_object('Option<ConsensusData>', data=ScaleBytes(bytes(result['result'])))

    #           # Decode the hex-encoded SCALE data (don't encode!)
    #           decoded_data = obj.decode()
    #           print("Decoded data:", decoded_data)

    #       except Exception as e:
    #           print("Decode error:", str(e))
