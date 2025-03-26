import asyncio
import json
import logging
import os
import time

import typer
import toml
from smp import header as smphdr
from smp import image_management as smpimg
from pathlib import Path

from smp.os_management import MCUMgrParametersReadResponse
from smpclient import SMPClient
from smpclient.transport.chirpstack_fuota import (SMPChirpstackFuotaTransport, DeploymentDevice,
                                                  ChirpstackFuotaDownlinkSpeed, ChirpstackFuotaMulticastGroupTypes)

from smpclient.requests.os_management import MCUMgrParametersRead

from chirpstack_fuota_client import DeviceService
from typing import Any, List

app = typer.Typer(name="chirpstack-fuota", help="Chirpstack FUOTA transport configuration group")

CONFIG_PATH: Path = Path.cwd() / "chirpstack_fuota.toml"

def load_config() -> dict:
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, 'r') as f:
            return toml.load(f)
    else:
        return {"chirpstack": {}, "fuota": {}}

def save_config(config: dict) -> None:
    with open(CONFIG_PATH, 'w') as f:
        toml.dump(config, f)

config = load_config()

@app.command('set-config-path')
def set_config_path(ctx: typer.Context, path: str) -> None:
    """Set the configuration file path."""
    global CONFIG_PATH
    CONFIG_PATH = Path(path)
    typer.echo(f"Configuration file path set to: {path}")

@app.command('set-server-addr')
def set_chirpstack_server_addr(ctx: typer.Context, address: str) -> None:
    """Set the Chirpstack server address."""
    config['chirpstack']['server_addr'] = address
    save_config(config)
    typer.echo(f"Chirpstack server address set to: {address}")

@app.command('get-server-addr')
def get_chirpstack_server_addr(ctx: typer.Context) -> None:
    """Get the Chirpstack server address."""
    address = config['chirpstack'].get('server_addr')
    if address:
        typer.echo(f"Chirpstack server address: {address}")
    else:
        typer.echo("Chirpstack server address not set")

@app.command('set-server-api-token')
def set_chirpstack_server_api_token(ctx: typer.Context, token: str) -> None:
    """Set the Chirpstack server API token."""
    config['chirpstack']['api_token'] = token
    save_config(config)
    typer.echo("Chirpstack server API token set")

@app.command('get-server-api-token')
def get_chirpstack_server_api_token(ctx: typer.Context) -> None:
    """Get the Chirpstack server API token."""
    token = config['chirpstack'].get('api_token')
    if token:
        typer.echo("Chirpstack server API token set")
    else:
        typer.echo("Chirpstack server API token not set")

@app.command('set-fuota-server-addr')
def set_chirpstack_app_server_addr(ctx: typer.Context, address: str) -> None:
    """Set the Chirpstack FUOTA application server address."""
    config['fuota']['server_addr'] = address
    save_config(config)
    typer.echo(f"Chirpstack FUOTA application server address set to: {address}")

@app.command('get-fuota-server-addr')
def get_chirpstack_app_server_addr(ctx: typer.Context) -> None:
    """Get the Chirpstack FUOTA application server address."""
    address = config['fuota'].get('server_addr')
    if address:
        typer.echo(f"Chirpstack FUOTA application server address: {address}")
    else:
        typer.echo("Chirpstack FUOTA application server address not set")

@app.command('set-app-id')
def set_chirpstack_app_id(ctx: typer.Context, app_id: str) -> None:
    """Set the Chirpstack application ID."""
    config['fuota']['app_id'] = app_id
    save_config(config)
    typer.echo(f"Chirpstack application ID set to: {app_id}")

@app.command('get-app-id')
def get_chirpstack_app_id(ctx: typer.Context) -> None:
    """Get the Chirpstack application ID."""
    app_id = config['fuota'].get('app_id')
    if app_id:
        typer.echo(f"Chirpstack application ID: {app_id}")
    else:
        typer.echo("Chirpstack application ID not set")

@app.command('get-deployment-devices')
def get_chirpstack_deployment_devices(ctx: typer.Context) -> None:
    """Get the list of Chirpstack deployment devices."""
    devices = config['fuota'].get('deployment_devices', [])
    typer.echo(f"Chirpstack deployment devices: {devices}")
    for device in devices:
        typer.echo(f"Device EUI: {device['dev_eui']}")

@app.command('add-deployment-device')
def add_chirpstack_deployment_device(ctx: typer.Context, dev_eui: str, gen_app_key: str) -> None:
    """Add a Chirpstack deployment device."""
    devices = config['fuota'].get('deployment_devices', [])
    if any(device["dev_eui"] == dev_eui for device in devices):
        typer.echo(f"Device with EUI {dev_eui} already exists.")
        return
    deployment_device = {"dev_eui": dev_eui, "gen_app_key": gen_app_key}
    devices.append(deployment_device)
    config['fuota']['deployment_devices'] = devices
    save_config(config)
    typer.echo(f"Chirpstack deployment device added: {dev_eui}")

@app.command('remove-deployment-device')
def remove_chirpstack_deployment_device(ctx: typer.Context, dev_eui: str) -> None:
    """Remove a Chirpstack deployment device."""
    devices = config['fuota'].get('deployment_devices', [])
    devices = [device for device in devices if device["dev_eui"] != dev_eui]
    config['fuota']['deployment_devices'] = devices
    save_config(config)
    typer.echo(f"Chirpstack deployment device removed: {dev_eui}")

@app.command('set-downlink-speed')
def set_chirpstack_downlink_speed(ctx: typer.Context, speed: ChirpstackFuotaDownlinkSpeed) -> None:
    """Set the Chirpstack FUOTA downlink speed."""
    config['fuota']['downlink_speed'] = speed.value
    save_config(config)
    typer.echo(f"Chirpstack FUOTA downlink speed set to: {speed}")

@app.command('get-downlink-speed')
def get_chirpstack_downlink_speed(ctx: typer.Context) -> None:
    """Get the Chirpstack FUOTA downlink speed."""
    speed = config['fuota'].get('downlink_speed')
    if speed:
        typer.echo(f"Chirpstack FUOTA downlink speed: {speed}")
    else:
        typer.echo("Chirpstack FUOTA downlink speed not set")

@app.command('set-multicast-group-type')
def set_chirpstack_multicast_group_type(ctx: typer.Context, multicast_group_type: ChirpstackFuotaMulticastGroupTypes) -> None:
    """Set the Chirpstack FUOTA multicast group type."""
    config['fuota']['multicast_group_type'] = multicast_group_type.value
    save_config(config)
    typer.echo(f"Chirpstack FUOTA multicast group type set to: {multicast_group_type}")

@app.command('get-multicast-group-type')
def get_chirpstack_multicast_group_type(ctx: typer.Context) -> None:
    """Get the Chirpstack FUOTA multicast group type."""
    multicast_group_type = config['fuota'].get('multicast_group_type')
    if multicast_group_type:
        typer.echo(f"Chirpstack FUOTA multicast group type: {multicast_group_type}")
    else:
        typer.echo("Chirpstack FUOTA multicast group type not set")

def create_chirpstack_fuota_smp_transport(config_path: str = None) -> SMPChirpstackFuotaTransport:
    if config_path is None:
        config_path = CONFIG_PATH

    with open(config_path, 'r') as f:
        local_config = toml.load(f)

    logging.getLogger('chirpstack_fuota').setLevel(logging.WARN)

    chirpstack_config = local_config['chirpstack']
    fuota_config = local_config['fuota']
    tas_config = local_config['tas']
    return SMPChirpstackFuotaTransport(
        multicast_group_type=fuota_config.get('multicast_group_type'),
        chirpstack_server_addr=chirpstack_config.get('server_addr'),
        chirpstack_server_api_token=chirpstack_config.get('api_token'),
        chirpstack_fuota_server_addr=fuota_config.get('server_addr'),
        chirpstack_server_app_id=fuota_config.get('app_id'),
        devices=fuota_config.get('deployment_devices', []),
        downlink_speed=fuota_config.get('downlink_speed'),
        tas_api_addr=tas_config.get('server_addr'),
        tas_api_lns_id=tas_config.get('lns_id'),
    )


@app.command('verify-app-id')
def verify_chirpstack_app_id(ctx: typer.Context) -> None:
    """Verify the Chirpstack application ID."""
    # Implementation to verify the Chirpstack application ID

    app_id =  config['fuota'].get('app_id')
    if app_id is None:
        typer.echo("Chirpstack application ID not set")
        return

    transport = create_chirpstack_fuota_smp_transport()
    if transport:
        async def f() -> bool:
            return await transport.verify_app_id(app_id)

        if asyncio.run(f()):
            typer.echo(f"Chirpstack application ID {app_id} verified")
        else:
            typer.echo(f"Chirpstack application ID {app_id} not verified")

@app.command('verify-deployment-devices')
def verify_chirpstack_deployment_devices(ctx: typer.Context) -> None:
    """Verify the Chirpstack deployment devices."""
    # Implementation to verify the Chirpstack deployment devices

    deployment_devices = config['fuota'].get('deployment_devices', [])
    if deployment_devices is None:
        typer.echo("Chirpstack deployment devices not set")
        return

    transport = create_chirpstack_fuota_smp_transport()
    if transport:
        async def f() -> List[DeploymentDevice]:
            return await transport.get_matched_devices()

        matched_devices = asyncio.run(f())

        if len(matched_devices) == len(deployment_devices):
            typer.echo("All deployment devices verified")
        else:
            typer.echo("Not all deployment devices were verified")

            # Find devices that are in deployment_devices but not in matched_devices
            deployment_dev_euis = {device["dev_eui"] for device in deployment_devices}
            matched_dev_euis = {device["dev_eui"] for device in matched_devices}
            unmatched_dev_euis = deployment_dev_euis - matched_dev_euis

            typer.echo("Unmatched deployment devices:")
            for device in deployment_devices:
                if device["dev_eui"] in unmatched_dev_euis:
                    typer.echo(f"Device EUI: {device['dev_eui']}")

@app.command('test-dummy-send')
def test_dummy_deployment(ctx: typer.Context, size: int, config_file_path: str) -> None:
    """Test a dummy firmware image send."""
    # Implementation to test a dummy deployment

    # Random bytes
    dummy_data = os.urandom(size)

    transport = create_chirpstack_fuota_smp_transport(config_file_path)

    if transport:
        local_smpclient = SMPClient(transport=transport, address="localhost:8080")

        async def f(smpclient: SMPClient) -> None:
            await smpclient.connect()

            typer.echo("Dummy send starting...")

            async for offset in smpclient.upload(dummy_data, first_timeout_s=1000.0, subsequent_timeout_s=1000.0):
                typer.echo(f"Uploading {offset=}")

        asyncio.run(f(local_smpclient))

        typer.echo("Dummy send completed")

@app.command('get-deployment-status')
def get_deployment_status(ctx: typer.Context, id: str, config_file_path: str) -> Any:
    """Get the deployment status."""
    # Implementation to get the deployment status
    transport = create_chirpstack_fuota_smp_transport(config_file_path)

    local_smpclient = SMPClient(transport=transport, address="localhost:8080")

    async def f(smpclient: SMPClient) -> Any:
        await smpclient.connect()

        typer.echo("Dummy send starting...")

        return await transport.get_deployment_status(id)

    status = asyncio.run(f(local_smpclient))

    # This is a placeholder implementation
    typer.echo(f"Deployment status: {status}")

@app.command('print-sample-uplink-sizes')
def print_sample_packet_sizes(ctx: typer.Context) -> None:
    """Print sample packet sizes for different Chirpstack FUOTA configurations."""
    # Implementation to print sample packet sizes

    # Create dummy image states

    image_state_1 = smpimg.ImageState(slot=0, version='0.2.1', hash=b'\x01' * 32, bootable=True, pending=False, confirmed=True, active=True, permanent=False)
    image_state_2 = smpimg.ImageState(slot=1, version='0.3.0', hash=b'\x02' * 32, bootable=True, pending=True, confirmed=False, active=False, permanent=False)

    response = smpimg.ImageStatesReadResponse(images=[image_state_1, image_state_2], splitStatus=0)

    for image in response.images:
        print(image)

    typer.echo(f"ImageStateReadResponse len: {len(response.BYTES)} Header size: {response.header.SIZE} ")

@app.command('get-mcumgr-parameters')
def get_mcumgr_parameters(ctx: typer.Context, config_file_path: str, dev_eui: str) -> None:

    transport = create_chirpstack_fuota_smp_transport(config_file_path)

    if transport:
        typer.echo("Creating mcumgr request")

        async def f(local_transport: SMPChirpstackFuotaTransport) -> None:
            mcumgr_request = MCUMgrParametersRead()
            typer.echo(f"Request: {mcumgr_request}, size: {len(mcumgr_request.BYTES)}")
            await local_transport.send_unicast(dev_eui, mcumgr_request.BYTES, 2)
            typer.echo("Request sent, waiting for response...")
            frame = await local_transport.receive_unicast(int(time.time()) - 30 , dev_eui, 2, 30.0)
            mcumgr_response = MCUMgrParametersReadResponse.loads(frame)
            typer.echo(f"Response: {mcumgr_response}")

        asyncio.run(f(transport))