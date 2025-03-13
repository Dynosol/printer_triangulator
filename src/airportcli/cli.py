#!/usr/bin/env python3
import threading
import time
import argparse
import re
from airportcli import get_available_networks, get_current_connection

def ping_thread(amount=1):
    count = 0
    while count < amount or amount == 0:
        ping = get_available_networks()
        print(ping)
        count += 1
        if count < amount or amount == 0:
            time.sleep(2)

def display_networks():
    """Display available networks in a tabular format similar to airport -s"""
    networks = get_available_networks()
    if not networks:
        print("No networks found.")
        return
    
    # Print header with indentation
    print("    SSID                      BSSID             RSSI CHANNEL HT CC SECURITY (auth/unicast/group)")
    
    # Print each network
    for network in networks:
        try:
            ssid = network.get("_name", "")
            bssid = network.get("spairport_bssid", "")
            
            # Extract RSSI from signal noise string (remove dBm)
            signal_noise = network.get("spairport_signal_noise", "")
            rssi_match = re.search(r'(-\d+)\s*dBm', signal_noise)
            rssi = rssi_match.group(1) if rssi_match else ""
            
            # Extract channel information
            channel_info = network.get("spairport_network_channel", "")
            # Extract just the channel number
            channel_match = re.search(r'(\d+(?:,\s*-?\d+)?)', channel_info)
            channel = channel_match.group(1) if channel_match else ""
            
            # Other information
            ht = "Y" if network.get("spairport_ht_capable", False) else "N"
            cc = network.get("spairport_country_code", "--")
            
            # Parse security mode
            security_mode = network.get("spairport_security_mode", "")
            security = parse_security_mode(security_mode)
            
            # Format the output with proper spacing and indentation
            print(f"    {ssid:<25} {bssid:<18} {rssi:<4} {channel:<7} {ht:<2} {cc:<2} {security}")
        except Exception as e:
            continue

def display_current_connection():
    """Display information about the current wireless connection"""
    connection = get_current_connection()
    if not connection:
        print("Not connected to any wireless network.")
        return
    
    # Extract signal and noise levels from signal_noise string
    signal_noise = connection.get("spairport_signal_noise", "")
    signal_match = re.search(r'(-\d+)\s*dBm', signal_noise)
    noise_match = re.search(r'/ (-\d+)\s*dBm', signal_noise)
    
    signal_level = signal_match.group(1) if signal_match else "0"
    noise_level = noise_match.group(1) if noise_match else "0"
    
    # Get other connection details
    bssid = connection.get("spairport_bssid", "")
    ssid = connection.get("_name", "")
    security_mode = connection.get("spairport_security_mode", "")
    security = parse_security_mode(security_mode)
    tx_rate = connection.get("spairport_network_rate", "0")
    
    # Get channel and band information
    channel_info = connection.get("spairport_network_channel", "")
    channel_match = re.search(r'(\d+)', channel_info)
    channel = channel_match.group(1) if channel_match else ""
    
    # Get phy mode
    phy_mode = connection.get("spairport_network_phymode", "")
    
    # Define the fields and values with the correct key names
    fields = {
        "agrCtlRSSI": signal_level,
        "agrCtlNoise": noise_level,
        "state": "running",
        "op mode": "station",
        "lastTxRate": str(tx_rate),
        "maxRate": str(tx_rate),
        "802.11 auth": phy_mode,
        "link auth": security,
        "BSSID": bssid,
        "SSID": ssid,
        "channel": channel
    }
    
    # Find the longest field name to determine proper alignment
    max_field_length = max(len(field) for field in fields.keys())
    
    # Print each field with proper alignment
    for field, value in fields.items():
        # Right-align the key, left-align the value with a space after the colon
        print(f"{field:>{max_field_length}} : {value}")

def parse_security_mode(security_mode):
    """Parse security mode into auth/unicast/group format"""
    if not security_mode:
        return "none"
    
    # Handle the raw security mode strings from the output
    if security_mode == "spairport_security_mode_wpa2_personal":
        return "WPA2(PSK/AES/AES)"
    elif security_mode == "spairport_security_mode_wpa2_enterprise":
        return "WPA2(802.1X/AES/AES)"
    elif security_mode == "spairport_security_mode_wpa3_personal":
        return "WPA3(SAE/AES/AES)"
    elif security_mode == "spairport_security_mode_wpa_personal":
        return "WPA(PSK/TKIP/TKIP)"
    elif security_mode == "spairport_security_mode_wpa_enterprise":
        return "WPA(802.1X/TKIP/TKIP)"
    elif security_mode == "spairport_security_mode_none" or "Open" in security_mode:
        return "none"
    else:
        # Return the raw mode if no specific pattern matches
        return security_mode

def main(num_threads=1, duration_seconds=None, amount=1):
    # Create and start multiple ping threads
    threads = []
    for _ in range(num_threads):
        thread = threading.Thread(target=ping_thread, args=(amount,), daemon=True)
        thread.start()
        threads.append(thread)
        # Small delay to stagger the starts
        time.sleep(2)
    
    try:
        # Keep the main thread alive for specified duration or until threads complete
        start_time = time.time()
        while True:
            # Check if all threads have finished
            if all(not t.is_alive() for t in threads):
                break
            # Check duration timeout
            if duration_seconds and (time.time() - start_time) >= duration_seconds:
                break
            time.sleep(0.1)  # Small sleep to prevent CPU spinning
    except KeyboardInterrupt:
        print("Exiting...")

def cli():
    parser = argparse.ArgumentParser(description='Airport network scanner')
    parser.add_argument('-s', '--scan', action='store_true',
                      help='Scan for wireless networks and display in tabular format')
    parser.add_argument('-I', '--info', action='store_true',
                      help='Display information about the current wireless connection')
    parser.add_argument('--num-threads', type=int, default=1,
                      help='Number of concurrent ping threads (default: 3)')
    parser.add_argument('--duration', type=int, default=None,
                      help='Duration to run in seconds (default: run indefinitely)')
    parser.add_argument('--amount', type=int, default=1,
                      help='Number of times to collect data (default: 1, 0 for infinite)')
    
    args = parser.parse_args()
    
    if args.scan:
        display_networks()
    elif args.info:
        display_current_connection()
    else:
        main(num_threads=args.num_threads, duration_seconds=args.duration, amount=args.amount)

if __name__ == "__main__":
    cli()
