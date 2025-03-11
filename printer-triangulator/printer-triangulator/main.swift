import Foundation
import CoreWLAN

class NetworkScanner {
    var currentInterface: CWInterface
    
    init?() {
        // Initialize with the default Wi-Fi interface
        guard let defaultInterface = CWWiFiClient.shared().interface(),
              defaultInterface.interfaceName != nil else {
            return nil
        }
        self.currentInterface = defaultInterface
        
        // Print the currently connected network, if any
        if let currentSSID = currentInterface.ssid() {
            print("Currently connected to: \(currentSSID)")
        } else {
            print("Not connected to any Wi-Fi network")
        }
        
        self.scanForNetworks()
    }
    
    func scanForNetworks() {
        do {
            let networks = try currentInterface.scanForNetworks(withName: nil)
            for network in networks {
                let ssid = network.ssid ?? "Unknown"
                let bssid = network.bssid ?? "Unknown"
                let rssi = network.rssiValue
                print("SSID: \(ssid), BSSID: \(bssid), RSSI: \(rssi)")
            }
        } catch let error as NSError {
            print("Error: \(error.localizedDescription)")
        }
    }
}

_ = NetworkScanner()
