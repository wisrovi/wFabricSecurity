"""
Pytest configuration and fixtures for wFabricSecurity tests.
"""

import os
import sys
import time
import multiprocessing
import pytest
import requests
from typing import Generator

sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
)


FABRIC_MSP_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
    "enviroment",
    "organizations",
    "peerOrganizations",
    "org1.net",
    "users",
    "Admin@org1.net",
    "msp",
)


def run_slave_server(module_path: str, port: int):
    """Run a slave server in a subprocess."""
    import uvicorn
    from fastapi import FastAPI
    import hashlib
    import json
    from wFabricSecurity import FabricSecurity
    from pydantic import BaseModel

    sys.path.insert(0, os.path.dirname(module_path))
    module_name = os.path.basename(module_path)[:-3]
    spec = __import__(module_name, fromlist=["app"])
    app = spec.app

    uvicorn.run(app, host="127.0.0.1", port=port, log_level="error")


@pytest.fixture(scope="session")
def msp_path():
    """Return the MSP path for testing."""
    return FABRIC_MSP_PATH


@pytest.fixture(scope="session")
def fabric_gateway(msp_path):
    """Create a FabricGateway for testing."""
    from wFabricSecurity.fabric_security.fabric_security import FabricGateway

    gateway = FabricGateway(peer_url="localhost:7051", msp_path=msp_path)
    return gateway


@pytest.fixture
def slave_server():
    """Fixture that provides a slave server manager."""
    processes = []

    class SlaveServerManager:
        def __init__(self):
            self.port = None
            self.process = None

        def start(self, module_path: str, port: int):
            self.port = port
            ctx = multiprocessing.get_context("spawn")
            self.process = ctx.Process(
                target=run_slave_server, args=(module_path, port)
            )
            self.process.start()
            processes.append(self.process)
            time.sleep(2)
            return self

        def get_url(self):
            return f"http://127.0.0.1:{self.port}/process"

        def health_check(self):
            try:
                resp = requests.get(f"http://127.0.0.1:{self.port}/health", timeout=5)
                return resp.status_code == 200
            except:
                return False

        def stop(self):
            if self.process:
                self.process.terminate()
                self.process.join(timeout=5)

    yield SlaveServerManager()

    for p in processes:
        p.terminate()
        p.join(timeout=5)


@pytest.fixture
def master_config():
    """Configuration for master tests."""
    return {
        "me": "MASTER_TEST",
        "peer_url": "localhost:7051",
        "msp_path": FABRIC_MSP_PATH,
    }
