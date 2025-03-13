#!/usr/bin/env python3

# regex for printer names: (?i)(DIRECT[\-_][A-F0-9]{2,6}[\-_])?(?:(HP|Canon|Brother|Epson|Xerox|Lexmark|Ricoh|Kyocera|Samsung|Dell|Konica|Minolta|Sharp|Toshiba|Oki|Panasonic|Fuji|Kodak|Zebra)[\s\-_]+)?((?:[A-Z0-9]+[\s\-_]+){1,4}(?:Pro|Plus|Max|Series|All[\s\-_]+in[\s\-_]+One|AIOne|MFP|Printer|Copier|Scanner|Fax|Wireless|WiFi|Print|Scan|Copy)?)
import subprocess
import json
import logging
from collections import defaultdict

# Setup logging configuration.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

def simplify(item):
    """
    Recursively simplify the structure by replacing any list
    containing a single element with that element.
    """
    if isinstance(item, list):
        if len(item) == 1:
            return simplify(item[0])
        else:
            return [simplify(subitem) for subitem in item]
    elif isinstance(item, dict):
        return {key: simplify(value) for key, value in item.items()}
    else:
        return item

def get_airport_data():
    """
    Get raw airport data from system_profiler.
    Returns the simplified interface data.
    """
    command = ["system_profiler", "-json", "SPAirPortDataType"]

    try:
        result = subprocess.run(
            command, capture_output=True, text=True, check=True
        )
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running command: {e}")
        return None

    try:
        plist_data_raw = json.loads(result.stdout)
        plist_data = simplify(plist_data_raw)

        airport_data = plist_data.get("SPAirPortDataType")
        if not airport_data:
            logger.error("No SPAirPortDataType found!")
            return None

        interfaces = airport_data.get("spairport_airport_interfaces")
        if isinstance(interfaces, list):
            # If you expect only one interface, you can take the first one:
            interface = interfaces[0]
        else:
            interface = interfaces

        return interface
    except Exception as e:
        logger.error(f"Error extracting airport data: {e}")
        return None

def get_available_networks():
    """
    Get information about available wireless networks.
    Returns a list of available networks.
    """
    interface = get_airport_data()
    if not interface:
        return None
    
    return interface.get("spairport_airport_other_local_wireless_networks")

def get_current_connection():
    """
    Get information about the current wireless connection.
    Returns a dictionary with current connection details.
    """
    interface = get_airport_data()
    if not interface:
        return None
    
    current_network = interface.get("spairport_current_network_information")
    if isinstance(current_network, list):
        current_network = current_network[0]
    
    if not current_network:
        logger.info("Not connected to any wireless network")
        return None

    return current_network