import os

import pytest
import asyncio
from smpmgr.common import Options, TransportDefinition, get_smpclient
from smpclient.transport.chirpstack_fuota import SMPChirpstackFuotaTransport

def test_get_smpclient_chirpstack_fuota():

    config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'chirpstack_fuota.toml'))

    options = Options(
        timeout=60.0,
        transport=TransportDefinition(
            port=None,
            ble=None,
            chirpstack_fuota=config_path
        ),
        mtu=2560
    )

    smpclient = get_smpclient(options)
    assert isinstance(smpclient._transport, SMPChirpstackFuotaTransport)
    assert smpclient._transport._chirpstack_server_addr == "54.166.56.164:8080"
    assert smpclient._transport.mtu == 1024

@pytest.mark.asyncio
async def test_connect():
    config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'chirpstack_fuota.toml'))

    options = Options(
        timeout=60.0,
        transport=TransportDefinition(
            port=None,
            ble=None,
            chirpstack_fuota=config_path
        ),
        mtu=2560
    )

    smpclient = get_smpclient(options)
    await smpclient.connect()
    assert smpclient._transport._chirpstack_server_addr == "54.166.56.164:8080"