import pytest
from smpmgr.common import Options, TransportDefinition, get_smpclient
from smpclient.transport.chirpstack_fuota import SMPChirpstackFuotaTransport

def test_get_smpclient_chirpstack_fuota():
    options = Options(
        timeout=60.0,
        transport=TransportDefinition(
            port=None,
            ble=None,
            chirpstack_fuota="localhost:8080"
        ),
        mtu=2560
    )

    smpclient = get_smpclient(options)
    assert isinstance(smpclient._transport, SMPChirpstackFuotaTransport)
    assert smpclient._transport._chirpstack_server_addr == "localhost:8080"
    assert smpclient._transport.mtu == 1024