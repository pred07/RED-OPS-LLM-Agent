import xml.etree.ElementTree as ET
from typing import Dict, Any
from core.state_manager import StateManager

class NmapParser:
    def __init__(self, state_manager: StateManager):
        self.sm = state_manager

    def parse_file(self, file_path: str):
        """Parses an Nmap XML file and updates the global state."""
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()

            for host in root.findall('host'):
                ip = host.find('address').get('addr')
                status = host.find('status').get('state')
                
                if status != 'up':
                    continue

                ports_data = {}
                ports_elem = host.find('ports')
                if ports_elem is not None:
                    for port in ports_elem.findall('port'):
                        portid = port.get('portid')
                        state = port.find('state').get('state')
                        
                        if state == 'open':
                            service_elem = port.find('service')
                            service_name = service_elem.get('name') if service_elem is not None else "unknown"
                            product = service_elem.get('product') if service_elem is not None else ""
                            version = service_elem.get('version') if service_elem is not None else ""
                            
                            ports_data[portid] = {
                                "service": service_name,
                                "product": product,
                                "version": version
                            }

                # Update the state manager with discovered ports
                if ports_data:
                    self.sm.update_target(ip, {"ports": ports_data})
                    print(f"[+] Parsed {len(ports_data)} open ports for {ip}")

            self.sm.save()
            return True
        except Exception as e:
            print(f"[!] Error parsing Nmap XML: {e}")
            return False
