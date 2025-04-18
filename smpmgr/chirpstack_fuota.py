import asyncio
from pathlib import Path
from typing import Any, Dict, List

import tomli
import typer
from smpclient.transport.chirpstack_fuota import (
    ChirpstackFuotaDownlinkSpeed,
    ChirpstackFuotaMulticastGroupTypes,
    DeploymentDevice,
    SMPChirpstackFuotaTransport,
)


def load_config(config_path: Path = Path("chirpstack_fuota.toml")) -> Dict[str, Any]:
    """Load configuration from TOML file."""
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(config_path, "rb") as f:
        return tomli.load(f)


def create_chirpstack_fuota_smp_transport(
    config_path: Path = Path("chirpstack_fuota.toml"),
) -> SMPChirpstackFuotaTransport:
    """Create a Chirpstack FUOTA SMP transport using configuration from TOML file."""
    config = load_config(config_path)

    # Extract values from config
    chirpstack_config = config.get("chirpstack", {})
    fuota_config = config.get("fuota", {})
    tas_config = config.get("tas", {})

    # Convert deployment devices from TOML format to DeploymentDevice objects
    deployment_devices = []
    for device in fuota_config.get("deployment_devices", []):
        deployment_devices.append(
            DeploymentDevice(dev_eui=device["dev_eui"], gen_app_key=device["gen_app_key"])
        )

    return SMPChirpstackFuotaTransport(
        multicast_group_type=ChirpstackFuotaMulticastGroupTypes(
            fuota_config.get("multicast_group_type", "CLASS_C")
        ),
        chirpstack_server_addr=chirpstack_config.get("server_addr", "localhost:8080"),
        chirpstack_server_api_token=chirpstack_config.get("api_token", ""),
        chirpstack_fuota_server_addr=fuota_config.get("server_addr", "localhost:8070"),
        chirpstack_server_app_id=fuota_config.get("app_id", ""),
        devices=deployment_devices,
        downlink_speed=ChirpstackFuotaDownlinkSpeed(fuota_config.get("downlink_speed", "DL_SLOW")),
        tas_api_addr=tas_config.get("server_addr", "http://localhost:8002"),
        tas_api_lns_id=tas_config.get("lns_id", ""),
    )


app = typer.Typer(name="chirpstack-fuota", help="Chirpstack FUOTA transport configuration group")


@app.command('verify-app-id')
def verify_chirpstack_app_id(ctx: typer.Context) -> None:
    """Verify the Chirpstack application ID."""

    async def f() -> bool:
        transport = create_chirpstack_fuota_smp_transport()
        return await transport.verify_app_id(transport._chirpstack_server_app_id)

    result = asyncio.run(f())
    if result:
        typer.echo("Chirpstack application ID is valid")
    else:
        typer.echo("Chirpstack application ID is invalid")


@app.command('verify-deployment-devices')
def verify_chirpstack_deployment_devices(ctx: typer.Context) -> None:
    """Verify the Chirpstack deployment devices."""

    async def f() -> List[DeploymentDevice]:
        transport = create_chirpstack_fuota_smp_transport()
        return await transport.get_matched_devices()

    devices = asyncio.run(f())
    if devices:
        typer.echo("Chirpstack deployment devices are valid")
        for device in devices:
            typer.echo(f"Device EUI: {device['dev_eui']}")
    else:
        typer.echo("No valid Chirpstack deployment devices found")


@app.command('test-dummy-send')
def test_dummy_deployment(ctx: typer.Context, size: int) -> None:
    """Test sending dummy data to the Chirpstack deployment devices."""

    async def f() -> None:
        transport = create_chirpstack_fuota_smp_transport()
        data = b"0" * size
        await transport.send_multicast(data)

    asyncio.run(f())
    typer.echo("Dummy data sent successfully")
