from scanner import scan_wifi, scan_printers
import time

def main():
    try:
        while True:
            print("Scanning for devices...")
            
            # Scan for devices
            printers = scan_printers(ip_range='192.168.0.0/16')  # Broader IP range
            wifi_devices = scan_wifi()
            
            # Print Wi-Fi devices
            print("\nWi-Fi Devices:")
            for device in wifi_devices:
                strength_color = get_color_based_on_strength(device['rssi'])
                print(f"SSID: {device['ssid']}, RSSI: {strength_color}{device['rssi']} dBm\033[0m")
            
            # Print printer devices
            print("\nPrinters:")
            if printers:
                for printer in printers:
                    print(f"IP: {printer['ip']}, Ports: {printer['ports']}")
            else:
                print("No printers found")
            
            print("\nScan complete!\n---\n")
            time.sleep(10)  # Refresh every 10 seconds
    
    except KeyboardInterrupt:
        print("\nScan interrupted by user")
    except Exception as e:
        print(f"Error: {e}")

def get_color_based_on_strength(rssi):
    if rssi > -50:
        return '\033[92m'  # Green
    elif -70 < rssi <= -50:
        return '\033[93m'  # Yellow
    else:
        return '\033[91m'  # Red

if __name__ == "__main__":
    main()