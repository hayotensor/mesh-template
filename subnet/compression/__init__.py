"""
Compression strategies that reduce the network communication in .averaging, .optim and .moe
"""

from subnet.compression.adaptive import PerTensorCompression, RoleAdaptiveCompression, SizeAdaptiveCompression
from subnet.compression.base import CompressionBase, CompressionInfo, NoCompression, TensorRole
from subnet.compression.floating import Float16Compression, ScaledFloat16Compression
from subnet.compression.quantization import BlockwiseQuantization, Quantile8BitQuantization, Uniform8BitQuantization
from subnet.compression.serialization import (
    deserialize_tensor_stream,
    deserialize_torch_tensor,
    serialize_torch_tensor,
)
