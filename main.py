#!/usr/bin/env python3
import airport_scanner
import json
import requests

def get_location_by_ip():
    """Get approximate location based on IP address"""
    try:
        response = requests.get('https://ipinfo.io/json')
        if response.status_code == 200:
            data = response.json()
            location = {
                'city': data.get('city', 'Unknown'),
                'region': data.get('region', 'Unknown'),
                'country': data.get('country', 'Unknown'),
                'loc': data.get('loc', 'Unknown'),  # Latitude,Longitude
                'timezone': data.get('timezone', 'Unknown')
            }
            return location
        else:
            return {'error': f'Request failed with status code {response.status_code}'}
    except Exception as e:
        return {'error': str(e)}

def main():
    # Get only the network data
    network_data = airport_scanner.get_network_data()
    if network_data:
        # Get and print location information
        print("\nLocation Information:")
        location = get_location_by_ip()
        if 'error' not in location:
            print(f"  City: {location.get('city')}")
            print(f"  Region: {location.get('region')}")
            print(f"  Country: {location.get('country')}")
            print(f"  Coordinates: {location.get('loc')}")
            print(f"  Timezone: {location.get('timezone')}")
        else:
            print(f"  Error getting location: {location.get('error')}")
        
        # Print Current Network
        print("\nCurrent Network:")
        if network_data["networks"] and "currentNetwork" in network_data["networks"][0]:
            current = network_data["networks"][0]["currentNetwork"]
            print(f"  Name: {current.get('_name')}")
            print(f"  Channel: {current.get('spairport_network_channel')}")
            print(f"  Signal: {current.get('spairport_signal_noise')}")
        
        # Print Available Networks
        print("\nAvailable Networks:")
        if (network_data["networks"] and 
            "availableNetworks" in network_data["networks"][0] and 
            network_data["networks"][0]["availableNetworks"]):
            
            available_networks = network_data["networks"][0]["availableNetworks"]
            # Sort networks by signal strength (strongest first)
            sorted_networks = sorted(
                available_networks, 
                key=lambda x: int(x.get("spairport_signal_noise", "-100 dBm").split()[0]) 
                if isinstance(x.get("spairport_signal_noise"), str) else -100,
                reverse=True
            )
            
            for i, network in enumerate(sorted_networks, 1):
                print(f"  {i}. {network.get('_name', 'Unknown')}")
                print(f"     Channel: {network.get('spairport_network_channel', 'Unknown')}")
                print(f"     Signal: {network.get('spairport_signal_noise', 'Unknown')}")
                print(f"     Security: {network.get('spairport_security_mode', 'Unknown')}")
                print(f"     Type: {network.get('spairport_network_phymode', 'Unknown')}")
                print()
        else:
            print("  No available networks found")
        
        # Add location to the network data
        network_data['location'] = location
        
        # Save the combined data to a file
        with open("network_data.json", "w") as f:
            json.dump(network_data, f, indent=2, default=airport_scanner.custom_serializer)

if __name__ == "__main__":
    main()
