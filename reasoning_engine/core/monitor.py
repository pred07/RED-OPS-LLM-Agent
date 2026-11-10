import os
import time
import re
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from modules.parsers.nmap_xml import NmapParser
from core.state_manager import StateManager
from core.chat_manager import ChatManager

class ResultsHandler(FileSystemEventHandler):
    def __init__(self, sm: StateManager, cm: ChatManager):
        self.sm = sm
        self.cm = cm
        self.nmap_parser = NmapParser(sm)

    def on_created(self, event):
        if event.is_directory:
            return
        self._process_file(event.src_path)

    def on_modified(self, event):
        if event.is_directory:
            return
        self._process_file(event.src_path)

    def _process_file(self, file_path: str):
        filename = os.path.basename(file_path)
        print(f"[*] New/Modified file detected: {filename}")
        
        # Identification Logic
        if filename.endswith(".xml"):
            print(f"[*] Identified as XML. Attempting Nmap parsing...")
            self.nmap_parser.parse_file(file_path)
        
        elif filename.endswith(".log") or filename.endswith(".txt"):
            print(f"[*] Identified as Text/Log. Running regex extraction...")
            self._parse_text_log(file_path)

    def _parse_text_log(self, file_path: str):
        """Extracts findings from raw text logs using regex."""
        try:
            with open(file_path, "r") as f:
                lines = f.readlines()
            
            content = "".join(lines)
            findings = {"users": [], "creds": [], "ports": {}}
            target_ip = None

            # --- Target IP Discovery ---
            ip_match = re.search(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", content)
            if ip_match:
                target_ip = ip_match.group(1)

            # --- Tool Specific Logic ---
            for line in lines:
                # Nmap Ports (Resilient to proxychains)
                port_match = re.search(r"(\d+)/(tcp|udp)\s+open\s+([^\s]+)", line)
                if port_match:
                    port, proto, service = port_match.groups()
                    findings["ports"][port] = {"service": service}

                # Kerbrute / User Discovery
                user_match = re.search(r"\[\+\] Valid user:\s+([a-zA-Z0-9\._\-]+)@?", line)
                if user_match:
                    findings["users"].append(user_match.group(1))

                # Hydra / Password Cracking
                hydra_match = re.search(r"login:\s+([^\s]+)\s+password:\s+([^\s]+)", line)
                if hydra_match:
                    findings["creds"].append(f"{hydra_match.group(1)}:{hydra_match.group(2)}")

                # Dig / DNS AXFR
                dns_match = re.search(r"([a-zA-Z0-9\.\-]+\.[a-z]{2,})\.\s+\d+\s+IN\s+A\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", line)
                if dns_match:
                    hostname, found_ip = dns_match.groups()
                    print(f"[+] [Monitor] Discovered new host via DNS: {hostname} ({found_ip})")
                    self.sm.update_target(found_ip, {"hostname": hostname})

            if target_ip and findings["ports"]:
                self.sm.update_target(target_ip, {"ports": findings["ports"]})
                self.cm.add_message("tool", f"Target {target_ip}: Found {len(findings['ports'])} ports.", "Nmap")
                print(f"[+] [Monitor] Extracted {len(findings['ports'])} ports for {target_ip}.")

            # --- NetExec / CrackMapExec ---
            found_users = re.findall(r"\[\+\] [^\\]+\\([a-zA-Z0-9\._\-]+)", content)
            if found_users:
                findings["users"].extend(found_users)

            # Update Users/Creds in State
            if target_ip:
                update_data = {}
                if findings["users"]:
                    update_data["users"] = list(set(findings["users"]))
                    self.cm.add_message("tool", f"Target {target_ip}: Discovered users: {', '.join(update_data['users'])}", "NetExec")
                if findings["creds"]:
                    update_data["creds"] = list(set(findings["creds"]))
                    self.cm.add_message("tool", f"Target {target_ip}: Cracked credentials: {', '.join(update_data['creds'])}", "Hydra")
                
                if update_data:
                    self.sm.update_target(target_ip, update_data)
                    print(f"[+] [Monitor] Updated users/creds for {target_ip}.")

            # --- Access Detection ---
            admin_markers = ["Pwn3d!", "nt authority\\system", "uid=0(root)", "Success: Admin Access"]
            if any(marker in content for marker in admin_markers) and target_ip:
                self.sm.update_target(target_ip, {"access_level": "admin"})
                self.cm.add_message("tool", f"Target {target_ip}: [CRITICAL] Admin Access Gained!", "Sentinel")
                print(f"[!] [Monitor] ADMIN ACCESS DETECTED on {target_ip}")

            user_markers = ["SMB Session opened", "Logged in as", "Access granted", "shell opened"]
            if any(marker in content for marker in user_markers) and target_ip:
                current_target = self.sm.get_all_targets().get(target_ip, {})
                if current_target.get("access_level") != "admin":
                    self.sm.update_target(target_ip, {"access_level": "user"})
                    print(f"[+] [Monitor] USER ACCESS DETECTED on {target_ip}")

            self.sm.save()

        except Exception as e:
            print(f"[!] Error parsing text log: {e}")

class Monitor:
    def __init__(self, sm: StateManager, cm: ChatManager, watch_dir: str = "reasoning_engine/results"):
        self.sm = sm
        self.cm = cm
        self.watch_dir = watch_dir
        self.observer = Observer()

    def start(self):
        os.makedirs(self.watch_dir, exist_ok=True)
        event_handler = ResultsHandler(self.sm, self.cm)
        self.observer.schedule(event_handler, self.watch_dir, recursive=False)
        self.observer.start()
        print(f"[*] Sentinel Eye: Monitoring {self.watch_dir} for findings...")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.observer.stop()
        self.observer.join()
