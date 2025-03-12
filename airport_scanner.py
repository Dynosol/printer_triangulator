#!/usr/bin/env python3
import subprocess
import plistlib
import json
import sys
import logging
import datetime
import os
import time

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

def get_network_data():
    """
    Extract only network-related data (current network and available networks).
    Returns a simplified JSON with just the network information.
    """
    logger.info("Getting network data...")
    command = ["system_profiler", "-xml", "SPAirPortDataType"]

    try:
        result = subprocess.run(
            command, capture_output=True, text=True, check=True
        )
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running command: {e}")
        return None

    try:
        plist_data = plistlib.loads(result.stdout.encode("utf-8"))
        full_data = reorganize_data(plist_data)
        
        # Extract only the network information
        network_data = {
            "timestamp": full_data["metadata"]["timestamp"],  # This is likely a datetime object
            "networks": []
        }
        
        for interface in full_data.get("wirelessInterfaces", []):
            if interface.get("name") == "en0":  # Main WiFi interface
                interface_info = {
                    "interface": interface.get("name"),
                    "currentNetwork": interface.get("currentNetwork", {}),
                    "availableNetworks": interface.get("availableNetworks", [])
                }
                network_data["networks"].append(interface_info)
                break  # We typically only care about the main interface
                
        return network_data
        
    except Exception as e:
        logger.error(f"Error extracting network data: {e}")
        return None

def collect_airport_data(output_file="./airport_data.json"):
    """
    Collect AirPort data and save to a JSON file.
    Returns the collected data as a dictionary.
    """
    logger.info("Starting system profiler command...")
    command = ["system_profiler", "-xml", "SPAirPortDataType"]

    try:
        result = subprocess.run(
            command, capture_output=True, text=True, check=True
        )
        logger.info("System profiler command executed successfully.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running command: {e}")
        return None

    logger.info("Parsing the XML output into a Python data structure...")
    try:
        plist_data = plistlib.loads(result.stdout.encode("utf-8"))
        logger.info("Plist parsing successful.")
    except Exception as e:
        logger.error(f"Error parsing plist data: {e}")
        return None
    
    logger.info("Reorganizing data for better readability...")
    try:
        reorganized_data = reorganize_data(plist_data)
    except Exception as e:
        logger.error(f"Error reorganizing data: {e}")
        return None

    logger.info("Converting data structure to JSON format...")
    try:
        json_data = json.dumps(reorganized_data, indent=2, default=custom_serializer)
    except Exception as e:
        logger.error(f"Error converting data to JSON: {e}")
        return None

    logger.info(f"Writing JSON data to {output_file}...")
    try:
        with open(output_file, 'w') as f:
            f.write(json_data)
        logger.info(f"JSON data successfully written to {output_file}")
    except Exception as e:
        logger.error(f"Error writing to file: {e}")
        return None
    
    return reorganized_data

def run_continuously(interval=60, output_file="./airport_data.json"):
    """
    Run the data collection continuously at the specified interval (in seconds).
    """
    logger.info(f"Starting continuous monitoring with {interval}s interval")
    try:
        while True:
            collect_airport_data(output_file)
            logger.info(f"Waiting {interval} seconds until next collection...")
            time.sleep(interval)
    except KeyboardInterrupt:
        logger.info("Continuous monitoring stopped by user")
    except Exception as e:
        logger.error(f"Error in continuous monitoring: {e}")

def main():
    collect_airport_data()

if __name__ == "__main__":
    main()
