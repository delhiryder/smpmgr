#!/usr/bin/env python3
"""
Simple BLE test script for Zephyr device.
This script uses only the bleak library to connect to a Zephyr device
and interact with its GATT characteristics.
"""

import asyncio
import logging
import platform
import sys
from typing import List, Optional

from bleak import BleakClient, BleakScanner
from bleak.backends.device import BLEDevice
from bleak.exc import BleakError

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Device address
DEVICE_ADDRESS = "EE:67:F5:83:61:65"

# Service and characteristic UUIDs
# These are from the SMP service
SMP_SERVICE_UUID = "8d53dc1d-1db7-4cd3-868b-8a527460aa84"
SMP_CHARACTERISTIC_UUID = "da2e7828-fbce-4e01-ae9e-261174997c48"

MAX_RETRY_COUNT = 3
RETRY_DELAY = 2  # seconds
SCAN_TIMEOUT = 30.0  # seconds


async def discover_devices() -> List[BLEDevice]:
    """Discover all BLE devices."""
    logger.info("Starting BLE discovery...")
    try:
        # Use a different set of parameters for the BleakScanner.discover() method
        devices = await BleakScanner.discover(timeout=SCAN_TIMEOUT, detection_callback=None)
        logger.info(f"Discovered {len(devices)} devices")
        for device in devices:
            logger.info(f"Found device: {device.name or 'Unknown'} ({device.address})")
        return devices
    except Exception as e:
        logger.error(f"Error during discovery: {e}")
        return []


async def get_device_with_retry(
    address: str, max_retries: int = MAX_RETRY_COUNT
) -> Optional[BLEDevice]:
    """Try to find the device with retries."""
    for attempt in range(max_retries):
        try:
            logger.info(f"Scanning attempt {attempt + 1}/{max_retries} for device {address}...")

            # Print diagnostic information
            logger.info(f"Platform: {platform.system()} {platform.release()}")
            logger.info(f"Python version: {sys.version}")

            # Discover all devices
            devices = await discover_devices()

            # Look for our specific device
            for device in devices:
                if device.address.lower() == address.lower():
                    logger.info(
                        f"Found target device: {device.name or 'Unknown'} ({device.address})"
                    )
                    return device

            logger.warning(f"Device {address} not found on attempt {attempt + 1}")

            if attempt < max_retries - 1:
                logger.info(f"Waiting {RETRY_DELAY} seconds before next attempt...")
                await asyncio.sleep(RETRY_DELAY)

        except BleakError as e:
            logger.error(f"Bleak error during scan attempt {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(RETRY_DELAY)
        except Exception as e:
            logger.error(f"Unexpected error during scan attempt {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(RETRY_DELAY)

    return None


async def main() -> None:
    try:
        # Try to find the device with retries
        device = await get_device_with_retry(DEVICE_ADDRESS)

        if device is None:
            logger.error(f"Failed to find device {DEVICE_ADDRESS} after {MAX_RETRY_COUNT} attempts")
            return

        # Connect to the device
        try:
            async with BleakClient(device, timeout=30.0) as client:
                logger.info(f"Connected to {client.address}")

                # Get all services
                services = await client.get_services()
                logger.info("Services:")
                for service in services:
                    logger.info(f"  Service: {service.uuid}")
                    for char in service.characteristics:
                        logger.info(f"    Characteristic: {char.uuid}")
                        logger.info(f"      Properties: {char.properties}")

                # Check if the SMP service exists
                smp_service = None
                for service in services:
                    if service.uuid.lower() == SMP_SERVICE_UUID.lower():
                        smp_service = service
                        break

                if smp_service is None:
                    logger.error(f"SMP service {SMP_SERVICE_UUID} not found!")
                    return

                logger.info(f"Found SMP service: {smp_service.uuid}")

                # Check if the SMP characteristic exists
                smp_char = None
                for char in smp_service.characteristics:
                    if char.uuid.lower() == SMP_CHARACTERISTIC_UUID.lower():
                        smp_char = char
                        break

                if smp_char is None:
                    logger.error(f"SMP characteristic {SMP_CHARACTERISTIC_UUID} not found!")
                    return

                logger.info(f"Found SMP characteristic: {smp_char.uuid}")
                logger.info(f"Properties: {smp_char.properties}")

                # Try to read from the characteristic if it supports reading
                if "read" in smp_char.properties:
                    try:
                        logger.info("Reading from SMP characteristic...")
                        value = await client.read_gatt_char(smp_char)
                        logger.info(f"Read value: {value.hex()}")
                    except Exception as e:
                        logger.error(f"Error reading characteristic: {e}")
                else:
                    logger.info("Characteristic does not support reading")

                # Try to write to the characteristic if it supports writing
                if (
                    "write" in smp_char.properties
                    or "write-without-response" in smp_char.properties
                ):
                    try:
                        # Example data - replace with your actual data
                        data = bytes([0x01, 0x02, 0x03])
                        logger.info(f"Writing to SMP characteristic: {data.hex()}")

                        # Use write-without-response if available, otherwise use write
                        if "write-without-response" in smp_char.properties:
                            await client.write_gatt_char(smp_char, data, response=False)
                        else:
                            await client.write_gatt_char(smp_char, data)

                        logger.info("Write successful")
                    except Exception as e:
                        logger.error(f"Error writing to characteristic: {e}")
                else:
                    logger.info("Characteristic does not support writing")

                # Try to enable notifications if the characteristic supports it
                if "notify" in smp_char.properties:
                    try:
                        logger.info("Enabling notifications...")

                        def notification_handler(sender: int, data: bytearray) -> None:
                            logger.info(f"Notification from {sender}: {data.hex()}")

                        await client.start_notify(smp_char, notification_handler)
                        logger.info("Notifications enabled")

                        # Wait for a few seconds to receive notifications
                        logger.info("Waiting for notifications (5 seconds)...")
                        await asyncio.sleep(5)

                        # Stop notifications
                        await client.stop_notify(smp_char)
                        logger.info("Notifications disabled")
                    except Exception as e:
                        logger.error(f"Error with notifications: {e}")
                else:
                    logger.info("Characteristic does not support notifications")

        except BleakError as e:
            logger.error(f"Bleak connection error: {e}")
        except Exception as e:
            logger.error(f"Unexpected connection error: {e}")

    except Exception as e:
        logger.error(f"Main loop error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
