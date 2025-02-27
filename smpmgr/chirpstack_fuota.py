import asyncio
import os
import shelve
import typer
from pathlib import Path
from smpclient.transport.chirpstack_fuota import SMPChirpstackFuotaTransport, DeploymentDevice
from typing import Any, List

CHIRPSTACK_FUOTA_DB_PATH: Path = Path.home() / ".chirpstack_fuota.db"

def set_value(key: str, value: Any) -> None:
    with shelve.open(str(CHIRPSTACK_FUOTA_DB_PATH)) as db:
        db[key] = value

def get_value(key: str) -> str:
    with shelve.open(str(CHIRPSTACK_FUOTA_DB_PATH)) as db:
        return db.get(key, None)

app = typer.Typer(name="chirpstack-fuota", help="Chirpstack FUOTA transport configuration group")

@app.command('set-server-addr')
def set_chirpstack_server_addr(ctx: typer.Context, address: str) -> None:
    """Set the Chirpstack server address."""
    # Implementation to set the Chirpstack FUOTA server address
    set_value('chirpstack_server_addr', address)
    typer.echo(f"Chirpstack server address set to: {address}")

@app.command('get-server-addr')
def get_chirpstack_server_addr(ctx: typer.Context) -> None:
    """Get the Chirpstack server address."""
    address = get_value('chirpstack_server_addr')
    if address:
        typer.echo(f"Chirpstack server address: {address}")
    else:
        typer.echo("Chirpstack server address not set")

@app.command('set-server-api-token')
def set_chirpstack_server_api_token(ctx: typer.Context, token: str) -> None:
    """Set the Chirpstack server API token."""
    # Implementation to set the Chirpstack FUOTA server API token
    set_value('chirpstack_server_api_token', token)
    typer.echo("Chirpstack server API token set")

@app.command('get-server-api-token')
def get_chirpstack_server_api_token(ctx: typer.Context) -> None:
    """Get the Chirpstack server API token."""
    token = get_value('chirpstack_server_api_token')
    if token:
        typer.echo("Chirpstack server API token set")
    else:
        typer.echo("Chirpstack server API token not set")

@app.command('set-fuota-server-addr')
def set_chirpstack_app_server_addr(ctx: typer.Context, address: str) -> None:
    """Set the Chirpstack FUOTA application server address."""
    # Implementation to set the Chirpstack FUOTA application server address
    set_value('chirpstack_fuota_server_addr', address)
    typer.echo(f"Chirpstack FUOTA application server address set to: {address}")

@app.command('get-fuota-server-addr')
def get_chirpstack_app_server_addr(ctx: typer.Context) -> None:
    """Get the Chirpstack FUOTA application server address."""
    address = get_value('chirpstack_fuota_server_addr')
    if address:
        typer.echo(f"Chirpstack FUOTA application server address: {address}")
    else:
        typer.echo("Chirpstack FUOTA application server address not set")

@app.command('set-app-id')
def set_chirpstack_app_id(ctx: typer.Context, app_id: str) -> None:
    """Set the Chirpstack application ID."""
    # Implementation to set the Chirpstack application ID
    set_value('chirpstack_app_id', app_id)
    typer.echo(f"Chirpstack application ID set to: {app_id}")

@app.command('get-app-id')
def get_chirpstack_app_id(ctx: typer.Context) -> None:
    """Get the Chirpstack application ID."""
    app_id = get_value('chirpstack_app_id')
    if app_id:
        typer.echo(f"Chirpstack application ID: {app_id}")
    else:
        typer.echo("Chirpstack application ID not set")

@app.command('get-deployment-devices')
def get_chirpstack_deployment_devices(ctx: typer.Context) -> None:
    """Get the list of Chirpstack deployment devices."""
    # Implementation to list the Chirpstack deployment devices
    devices = get_value('chirpstack_deployment_devices')
    if devices is None:
        devices = []
        set_value('chirpstack_deployment_devices', devices)

    typer.echo(f"Chirpstack deployment devices: {devices}")

    for device in devices:
        typer.echo(f"Device EUI: {device['dev_eui']}")

@app.command('add-deployment-device')
def add_chirpstack_deployment_device(ctx: typer.Context, dev_eui: str, gen_app_key: str) -> None:
    """Add a Chirpstack deployment device."""
    # Implementation to add a Chirpstack deployment device
    devices = get_value('chirpstack_deployment_devices')
    if devices is None:
        devices = []

    # Check if dev_eui already exists
    if any(device["dev_eui"] == dev_eui for device in devices):
        typer.echo(f"Device with EUI {dev_eui} already exists.")
        return

    deployment_device = DeploymentDevice(dev_eui=dev_eui, gen_app_key=gen_app_key)
    devices.append(deployment_device)
    set_value('chirpstack_deployment_devices', devices)
    typer.echo(f"Chirpstack deployment device added: {dev_eui}")

@app.command('remove-deployment-device')
def remove_chirpstack_deployment_device(ctx: typer.Context, dev_eui: str) -> None:
    """Remove a Chirpstack deployment device."""
    # Implementation to remove a Chirpstack deployment device
    devices = get_value('chirpstack_deployment_devices')
    if devices is None:
        devices = []

    for device in devices:
        if device["dev_eui"] == dev_eui:
            devices.remove(device)
            break

    set_value('chirpstack_deployment_devices', devices)
    typer.echo(f"Chirpstack deployment device removed: {dev_eui}")


def create_chirpstack_fuota_smp_transport() -> SMPChirpstackFuotaTransport:
    # Implementation to create a Chirpstack FUOTA SMP transport
    chirpstack_server_addr = get_value('chirpstack_server_addr')
    chirpstack_server_api_token = get_value('chirpstack_server_api_token')
    chirpstack_fuota_server_addr = get_value('chirpstack_fuota_server_addr')
    chirpstack_app_id = get_value('chirpstack_app_id')
    deployment_devices = get_value('chirpstack_deployment_devices')

    return SMPChirpstackFuotaTransport(
        chirpstack_server_addr=chirpstack_server_addr,
        chirpstack_server_api_token=chirpstack_server_api_token,
        chirpstack_fuota_server_addr=chirpstack_fuota_server_addr,
        chirpstack_server_app_id=chirpstack_app_id,
        devices=deployment_devices,
    )


@app.command('verify-app-id')
def verify_chirpstack_app_id(ctx: typer.Context) -> None:
    """Verify the Chirpstack application ID."""
    # Implementation to verify the Chirpstack application ID

    app_id = get_value('chirpstack_app_id')
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

    deployment_devices = get_value('chirpstack_deployment_devices')
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
def test_dummy_deployment(ctx: typer.Context, size: int) -> None:
    """Test a dummy firmware image send."""
    # Implementation to test a dummy deployment

    # Random bytes
    dummy_data = os.urandom(size)

    transport = create_chirpstack_fuota_smp_transport()
    if transport:
        async def f() -> None:
            await transport.connect(get_value('chirpstack_fuota_server_addr'), 10.0)
            await transport.send(dummy_data)

        asyncio.run(f())
        typer.echo("Dummy send completed")