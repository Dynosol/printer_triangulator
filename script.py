#!/usr/bin/env python3
import subprocess
import plistlib
import json
import sys
import logging
import datetime
import os

# Setup logging configuration.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

def custom_serializer(obj):
    """Convert non-JSON serializable objects to a serializable format."""
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {obj.__class__.__name__} "
                    "is not JSON serializable")

def reorganize_data(data):
    """Reorganize data for better readability while preserving all information."""
    result = {
        "metadata": {
            "timestamp": data[0].get("_timeStamp"),
            "command": {
                "arguments": data[0].get("_SPCommandLineArguments"),
                "completionInterval": data[0].get("_SPCompletionInterval"),
                "responseTime": data[0].get("_SPResponseTime"),
                "dataType": data[0].get("_dataType"),
                "detailLevel": data[0].get("_detailLevel"),
            },
            "versionInfo": data[0].get("_versionInfo"),
            "properties": data[0].get("_properties"),
        },
        "wirelessInterfaces": []
    }
    
    items = data[0].get("_items", [])
    for item in items:
        if "spairport_software_information" in item:
            result["softwareInformation"] = item["spairport_software_information"]
            
        if "spairport_airport_interfaces" in item:
            for interface in item["spairport_airport_interfaces"]:
                interface_data = {
                    "name": interface.get("_name"),
                    "status": interface.get("spairport_status_information"),
                    "hardwareInfo": {
                        "cardType": interface.get("spairport_wireless_card_type"),
                        "macAddress": interface.get("spairport_wireless_mac_address"),
                        "firmwareVersion": interface.get("spairport_wireless_firmware_version"),
                        "countryCode": interface.get("spairport_wireless_country_code"),
                        "locale": interface.get("spairport_wireless_locale"),
                        "supportedPhyModes": interface.get("spairport_supported_phymodes")
                    },
                    "capabilities": {
                        "airdrop": interface.get("spairport_caps_airdrop"),
                        "autounlock": interface.get("spairport_caps_autounlock"),
                        "wakeOnWireless": interface.get("spairport_caps_wow")
                    },
                    "supportedChannels": interface.get("spairport_supported_channels", []),
                    "currentNetwork": interface.get("spairport_current_network_information", {})
                }
                
                # Add available networks if present
                if "spairport_airport_other_local_wireless_networks" in interface:
                    interface_data["availableNetworks"] = interface["spairport_airport_other_local_wireless_networks"]
                
                # Remove None values to clean up the output
                interface_data = {k: v for k, v in interface_data.items() if v is not None}
                result["wirelessInterfaces"].append(interface_data)
    
    # Preserve the original data too
    result["originalData"] = data
    
    return result

def main():
    # Define output file path in the current directory
    output_file = "./airport_data.json"
    
    logger.info("Starting system profiler command...")
    command = ["system_profiler", "-xml", "SPAirPortDataType"]

    try:
        result = subprocess.run(
            command, capture_output=True, text=True, check=True
        )
        logger.info("System profiler command executed successfully.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running command: {e}")
        sys.exit(1)

    logger.info("Parsing the XML output into a Python data structure...")
    try:
        plist_data = plistlib.loads(result.stdout.encode("utf-8"))
        logger.info("Plist parsing successful.")
    except Exception as e:
        logger.error(f"Error parsing plist data: {e}")
        sys.exit(1)
    
    logger.info("Reorganizing data for better readability...")
    try:
        reorganized_data = reorganize_data(plist_data)
    except Exception as e:
        logger.error(f"Error reorganizing data: {e}")
        sys.exit(1)

    logger.info("Converting data structure to JSON format...")
    try:
        json_data = json.dumps(reorganized_data, indent=2, default=custom_serializer)
    except Exception as e:
        logger.error(f"Error converting data to JSON: {e}")
        sys.exit(1)

    logger.info(f"Writing JSON data to {output_file}...")
    try:
        with open(output_file, 'w') as f:
            f.write(json_data)
        logger.info(f"JSON data successfully written to {output_file}")
    except Exception as e:
        logger.error(f"Error writing to file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
