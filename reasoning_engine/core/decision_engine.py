from typing import List, Dict, Any
from core.state_manager import StateManager

class DecisionEngine:
    def __init__(self, state_manager: StateManager):
        self.sm = state_manager

    def get_suggestions(self) -> List[Dict[str, Any]]:
        phase = self.sm.get_phase()
        targets = self.sm.get_all_targets()
        suggestions = []

        if not targets:
            return [{
                "priority": "CRITICAL",
                "phase": "DISCOVERY",
                "action": "Run Nmap Network Scan",
                "command": "nmap -sC -sV -oX scan.xml <target_range>",
                "why": "No targets found in state. Discovery is the first priority."
            }]

        for ip, data in targets.items():
            suggestions.extend(self._analyze_target(ip, data, phase))

        # Sort by priority
        priority_map = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        suggestions.sort(key=lambda x: priority_map.get(x["priority"], 99))

        return suggestions

    def _analyze_target(self, ip: str, data: Dict[str, Any], phase: str) -> List[Dict[str, Any]]:
        target_suggestions = []
        ports = data.get("ports", {})
        users = data.get("users", [])
        creds = data.get("creds", [])
        access = data.get("access_level")
        os_type = data.get("os", "Unknown")

        # --- PHASE 1: DISCOVERY & RECON (M3, M4, M5) ---
        if not self.sm.is_action_tried(f"full_port_scan_{ip}"):
            target_suggestions.append({
                "priority": "HIGH",
                "target": ip,
                "action": "Full 65k TCP Scan",
                "command": f"nmap -sC -sV -p- -T4 -Pn {ip}",
                "why": "Surface mapping: Ensuring no non-standard ports are missed."
            })

        # Web Recon
        if any(p in ports for p in ["80", "443", "8080", "8443"]):
            if not self.sm.is_action_tried(f"vhost_enum_{ip}"):
                target_suggestions.append({
                    "priority": "HIGH",
                    "target": ip,
                    "action": "VHost Enumeration (ffuf)",
                    "command": f"ffuf -w /usr/share/seclists/Discovery/DNS/namelist.txt -H 'Host: FUZZ.{ip}' -u http://{ip} -fs <size>",
                    "why": "Web detected. Finding hidden dev/staging sites on the same IP."
                })
            
            if not self.sm.is_action_tried(f"web_fuzz_{ip}"):
                target_suggestions.append({
                    "priority": "HIGH",
                    "target": ip,
                    "action": "Directory Fuzzing (Feroxbuster)",
                    "command": f"feroxbuster -u {'https' if '443' in ports else 'http'}://{ip} -w /usr/share/wordlists/dirb/common.txt",
                    "why": "Discovering hidden endpoints, backups, or sensitive config files."
                })

        # DNS Zone Transfer
        if "53" in ports and not self.sm.is_action_tried(f"dns_axfr_{ip}"):
            target_suggestions.append({
                "priority": "MEDIUM",
                "target": ip,
                "action": "DNS Zone Transfer (dig)",
                "command": f"dig axfr @{ip} <domain>",
                "why": "Attempting to dump the entire internal network map."
            })

        # --- PHASE 2: AUTH & ACCESS (M10, M11, M13) ---
        # SMB & AD Logic
        if "445" in ports:
            if not self.sm.is_action_tried(f"smb_null_{ip}"):
                target_suggestions.append({
                    "priority": "HIGH",
                    "target": ip,
                    "action": "SMB Null Session Check",
                    "command": f"rpcclient -U '' -N {ip} -c 'querydispinfo; enumdomusers'",
                    "why": "Checking for unauthenticated user enumeration via RPC/SMB."
                })
            
            if users and not creds:
                target_suggestions.append({
                    "priority": "CRITICAL",
                    "target": ip,
                    "action": "SMB Password Spray",
                    "command": f"nxc smb {ip} -u users.txt -p 'Spring2024!' --continue-on-success",
                    "why": "Known users found. Attempting low-velocity password spray."
                })

        # Kerberos Logic
        if "88" in ports:
            if not users:
                target_suggestions.append({
                    "priority": "HIGH",
                    "target": ip,
                    "action": "Kerberos User Enumeration",
                    "command": f"kerbrute userenum --dc {ip} -d <domain> userlist.txt",
                    "why": "Kerberos is open. Brute-forcing valid usernames for AD attacks."
                })
            elif users and not creds:
                target_suggestions.append({
                    "priority": "HIGH",
                    "target": ip,
                    "action": "AS-REP Roasting",
                    "command": f"GetNPUsers.py <domain>/ -usersfile users.txt -format hashcat",
                    "why": "Users found. Checking for accounts that don't require pre-auth."
                })

        # Database Takeover
        if "1433" in ports and not self.sm.is_action_tried(f"mssql_rce_{ip}"):
             target_suggestions.append({
                "priority": "HIGH",
                "target": ip,
                "action": "MSSQL RCE Check (xp_cmdshell)",
                "command": f"mssqlclient.py <user>@{ip} -windows-auth",
                "why": "MSSQL detected. If sysadmin, RCE can be gained via xp_cmdshell."
            })

        # --- PHASE 3: EXPANSION & PIVOTING (M12, M13) ---
        if access:
            # Privilege Escalation
            if access == "user" and not self.sm.is_action_tried(f"priv_esc_enum_{ip}"):
                target_suggestions.append({
                    "priority": "CRITICAL",
                    "target": ip,
                    "action": "PrivEsc Enumeration",
                    "command": "winPEAS.exe" if os_type == "Windows" else "./linpeas.sh",
                    "why": "User access gained. Searching for misconfigurations to reach Admin/Root."
                })

            # AD Mapping
            if os_type == "Windows" and not self.sm.is_action_tried(f"bloodhound_{ip}"):
                target_suggestions.append({
                    "priority": "HIGH",
                    "target": ip,
                    "action": "Run BloodHound Collector",
                    "command": "sharphound.exe -c All",
                    "why": "Mapping domain relationships to identify paths to Domain Admin."
                })

            # Pivoting
            if not self.sm.is_action_tried(f"pivot_check_{ip}"):
                target_suggestions.append({
                    "priority": "MEDIUM",
                    "target": ip,
                    "action": "Identify Pivot Points",
                    "command": "ipconfig /all" if os_type == "Windows" else "ip a",
                    "why": "Searching for secondary interfaces to pivot into internal subnets."
                })

        return target_suggestions

    def get_stuck_logic(self) -> List[Dict[str, Any]]:
        """Rule-based methodology audit when progress is stalled."""
        audit = []
        targets = self.sm.get_all_targets()

        if not targets:
            audit.append({"advice": "Verify network connectivity and re-run Nmap with -Pn."})
        
        for ip, data in targets.items():
            ports = data.get("ports", {})
            if "80" in ports or "443" in ports:
                audit.append({"target": ip, "advice": "Web detected. Check for subdomains (ffuf) and hidden files (feroxbuster)."})
            if "445" in ports:
                audit.append({"target": ip, "advice": "SMB detected. Have you checked for Null Sessions or guest access?"})
            
        return audit
