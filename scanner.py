import subprocess
import re

def get_wifi_networks():
    try:
        # Use the correct path: /usr/bin/wdutil
        result = subprocess.run(['sudo', '/usr/bin/wdutil', 'info'], 
                                capture_output=True, 
                                text=True, 
                                check=True)
        
        # Get the output
        output = result.stdout
        
        # Parse output for SSID and signal strength
        # This assumes wdutil info lists networks in a format like "SSID: <name>\nSignal: <value>"
        network_pattern = r'SSID\s*:\s*(.+?)\n(?:.*\n)*?Signal\s*:\s*(-?\d+)'
        networks = re.findall(network_pattern, output)
        
        if networks:
            print("Available Wi-Fi Networks:")
            print("------------------------")
            for ssid, signal in networks:
                print(f"SSID: {ssid.strip():<32} Signal: {signal} dBm")
        else:
            print("No Wi-Fi networks found in scan.")
            
    except subprocess.CalledProcessError as e:
        print(f"Error running wdutil: {e}")
        print(f"Output: {e.output}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    print("This script requires sudo privileges to scan Wi-Fi networks.")
    get_wifi_networks()