import codecs
import glob
import hashlib
import os
import platform
import re
import subprocess
import tarfile
import tempfile
import urllib.request

from pkg_resources import parse_requirements, parse_version
from setuptools import find_packages, setup
from setuptools.command.build_py import build_py
from setuptools.command.develop import develop
from setuptools.command.egg_info import egg_info

P2PD_VERSION = "v0.5.0.hivemind1"

# TODO: Update to our own repo
P2PD_SOURCE_URL = f"https://github.com/learning-at-home/go-libp2p-daemon/archive/refs/tags/{P2PD_VERSION}.tar.gz"
P2PD_BINARY_URL = f"https://github.com/learning-at-home/go-libp2p-daemon/releases/download/{P2PD_VERSION}/"

# The value is sha256 of the binary from the release page
P2P_BINARY_HASH = {
    "p2pd-darwin-amd64": "fe00f9d79e8e4e4c007144d19da10b706c84187b3fb84de170f4664c91ecda80",
    "p2pd-darwin-arm64": "0404981a9c2b7cab5425ead2633d006c61c2c7ec85ac564ef69413ed470e65bd",
    "p2pd-linux-amd64": "42f8f48e62583b97cdba3c31439c08029fb2b9fc506b5bdd82c46b7cc1d279d8",
    "p2pd-linux-arm64": "046f18480c785a84bdf139d7486086d379397ca106cb2f0191598da32f81447a",
}

here = os.path.abspath(os.path.dirname(__file__))


def sha256(path):
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def proto_compile(output_path):
    from grpc_tools import protoc

    proto_path = os.path.join(here, "subnet", "proto")
    proto_files = glob.glob(os.path.join(proto_path, "*.proto"))
    result = protoc.main(
        [
            "grpc_tools.protoc",
            f"--proto_path={proto_path}",
            f"--python_out={output_path}",
            *proto_files,
        ]
    )
    if result != 0:
        raise RuntimeError(f"protoc failed with exit code {result}")

    # Fix imports to be relative
    for py_file in glob.glob(f"{output_path}/*_pb2.py"):
        with open(py_file, "r+") as f:
            code = f.read()
            code = re.sub(r"^import (.+_pb2.*)", r"from . import \1", code, flags=re.MULTILINE)
            f.seek(0)
            f.write(code)
            f.truncate()


def build_p2p_daemon():
    result = subprocess.run("go version", capture_output=True, shell=True).stdout.decode("ascii", "replace")
    m = re.search(r"^go version go([\d.]+)", result)

    if m is None:
        raise FileNotFoundError("Could not find golang installation")
    version = parse_version(m.group(1))
    if version < parse_version("1.13"):
        raise OSError(f"Newer version of go required: must be >= 1.13, found {version}")

    with tempfile.TemporaryDirectory() as tempdir:
        dest = os.path.join(tempdir, "libp2p-daemon.tar.gz")
        urllib.request.urlretrieve(P2PD_SOURCE_URL, dest)

        with tarfile.open(dest, "r:gz") as tar:
            tar.extractall(tempdir)

        result = subprocess.run(
            ["go", "build", "-o", os.path.join(here, "subnet", "subnet_cli", "p2pd")],
            cwd=os.path.join(tempdir, f"go-libp2p-daemon-{P2PD_VERSION.lstrip('v')}", "p2pd"),
        )
        if result.returncode != 0:
            raise RuntimeError(f"Failed to build p2pd: exited with status code: {result.returncode}")


def download_p2p_daemon():
    binary_path = os.path.join(here, "subnet", "subnet_cli", "p2pd")
    arch = platform.machine()
    # An architecture name may vary depending on the OS (e.g., the same CPU is arm64 on macOS and aarch64 on Linux).
    # We consider multiple aliases here, see https://stackoverflow.com/questions/45125516/possible-values-for-uname-m
    if arch in ("x86_64", "x64"):
        arch = "amd64"
    if arch in ("aarch64", "aarch64_be", "armv8b", "armv8l"):
        arch = "arm64"
    binary_name = f"p2pd-{platform.system().lower()}-{arch}"

    if binary_name not in P2P_BINARY_HASH:
        raise RuntimeError(
            f"subnet does not provide a precompiled p2pd binary for {platform.system()} ({arch}). "
            f"Please install Go and build it from source: https://github.com/hypertensor-blockchain/subnet-template#from-source"
        )
    expected_hash = P2P_BINARY_HASH[binary_name]

    if sha256(binary_path) != expected_hash:
        binary_url = os.path.join(P2PD_BINARY_URL, binary_name)
        print(f"Downloading {binary_url} to {binary_path}")

        urllib.request.urlretrieve(binary_url, binary_path)
        os.chmod(binary_path, 0o777)

        actual_hash = sha256(binary_path)
        if actual_hash != expected_hash:
            raise RuntimeError(
                f"The sha256 checksum for p2pd does not match (expected: {expected_hash}, actual: {actual_hash})"
            )


class BuildPy(build_py):
    user_options = build_py.user_options + [("buildgo", None, "Builds p2pd from source")]

    def initialize_options(self):
        super().initialize_options()
        self.buildgo = False

    def run(self):
        if self.buildgo:
            build_p2p_daemon()
        else:
            download_p2p_daemon()

        super().run()
        print("Compiling proto files")
        proto_output_path = os.path.join(self.build_lib, "subnet", "proto")
        os.makedirs(proto_output_path, exist_ok=True)
        proto_compile(proto_output_path)


class Develop(develop):
    def run(self):
        # Ensure build_lib is set to the current directory for editable installs
        build_py_cmd = self.get_finalized_command("build_py")
        build_py_cmd.build_lib = here
        self.run_command("build_py")

        # Also compile proto files directly for editable installs
        # This ensures they're compiled even if build_py doesn't run as expected
        print("Compiling proto files for editable install")
        proto_output_path = os.path.join(here, "subnet", "proto")
        os.makedirs(proto_output_path, exist_ok=True)
        proto_compile(proto_output_path)

        super().run()


class EggInfo(egg_info):
    """Custom egg_info command that compiles proto files.
    This is called even with PEP 517 editable installs."""

    def run(self):
        print("EGG_INFO: Compiling proto files")
        proto_output_path = os.path.join(here, "subnet", "proto")
        os.makedirs(proto_output_path, exist_ok=True)
        proto_compile(proto_output_path)

        super().run()


with open("requirements.txt") as requirements_file:
    install_requires = list(map(str, parse_requirements(requirements_file)))

# loading version from setup.py
with codecs.open(os.path.join(here, "subnet/__init__.py"), encoding="utf-8") as init_file:
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", init_file.read(), re.MULTILINE)
    version_string = version_match.group(1)

extras = {}

with open("requirements-dev.txt") as dev_requirements_file:
    extras["dev"] = list(map(str, parse_requirements(dev_requirements_file)))

with open("requirements-docs.txt") as docs_requirements_file:
    extras["docs"] = list(map(str, parse_requirements(docs_requirements_file)))

extras["bitsandbytes"] = ["bitsandbytes~=0.45.2"]

extras["all"] = extras["dev"] + extras["docs"] + extras["bitsandbytes"]

setup(
    name="subnet",
    version=version_string,
    cmdclass={"build_py": BuildPy, "develop": Develop, "egg_info": EggInfo},
    description="Decentralized Artificial Intelligence App Template",
    long_description="Decentralized Artificial Intelligence App Template for building on top of Hypertensor.",
    author="Learning@home & contributors",
    author_email="subnet-team@hotmail.com",
    url="https://github.com/hypertensor-protocol/subnet-template",
    packages=find_packages(exclude=["tests"]),
    package_data={"subnet": ["proto/*", "subnet_cli/*", "bootnode_utils/*.json"]},
    include_package_data=True,
    license="MIT",
    setup_requires=["grpcio-tools"],
    install_requires=install_requires,
    extras_require=extras,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    entry_points={
        "console_scripts": [
            "subnet-dht = subnet.subnet_cli.run_dht:main",
            "subnet-dht-api = subnet.subnet_cli.run_dht_api:main",
            "subnet-server = subnet.subnet_cli.run_server:main",
            "subnet-server-mock = subnet.subnet_cli.run_server_mock:main",
            # DHT Bootnode API
            "subnet-add-api-key = subnet.subnet_cli.api.add_key:main",
            # generate in-subnet private key for peer identity
            "keygen = subnet.subnet_cli.crypto.keygen:main",
            # generate coldkey or hotkey
            "generate-key = subnet.subnet_cli.hypertensor.keys.generate_key:main",
            # view peer ID from private key
            "keyview = subnet.subnet_cli.crypto.keyview:main",
            # hypertensor subnet
            "register-subnet = subnet.subnet_cli.hypertensor.subnet.register:main",
            "activate-subnet = subnet.subnet_cli.hypertensor.subnet.activate:main",
            # hypertensor node
            "register-node = subnet.subnet_cli.hypertensor.node.register:main",
            "activate-node = subnet.subnet_cli.hypertensor.node.activate:main",
            "register-activate-node = subnet.subnet_cli.hypertensor.node.register_activate:main",
        ]
    },
    # What does your project relate to?
    keywords="pytorch, deep learning, machine learning, gpu, distributed computing, P2P, dht, decentralized",
)
