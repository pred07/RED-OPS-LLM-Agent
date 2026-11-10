import re
import os

class ReasoningEngine:
    def __init__(self, training_doc="docs-ref/attack_logic_training.md"):
        self.training_doc = training_doc
        self.vectors = self._parse_training_doc()

    def _parse_training_doc(self):
        """Extracts attack methods from the training markdown using multiple patterns."""
        vectors = []
        if not os.path.exists(self.training_doc):
            return []
            
        with open(self.training_doc, 'r') as f:
            content = f.read()
            
        # Pattern 1: Master Service Catalog Table
        # | **Port** | **Service** | Logic | Tooling |
        svc_matches = re.findall(r'\|\s*\*\*(.*?)\*\*\s*\|\s*\*\*(.*?)\*\*\s*\|\s*(.*?)\s*\|\s*`(.*?)`\s*\|', content)
        for m in svc_matches:
            # Tooling might be a list: `ssh`, `hydra`, `nxc ssh`
            tools = [t.strip().strip('`') for t in m[3].split(',')]
            for tool in tools:
                vectors.append({
                    "name": f"{m[1]} Attack: {tool.split()[0]}",
                    "port_hint": m[0],
                    "command": tool,
                    "desc": m[2]
                })

        # Pattern 2: Advanced Edge Cases Table
        # | **Target** | **Technique** | Tooling | Logic |
        edge_matches = re.findall(r'\|\s*\*\*(.*?)\*\*\s*\|\s*\*\*(.*?)\*\*\s*\|\s*`(.*?)`\s*\|\s*(.*?)\s*\|', content)
        for m in edge_matches:
            vectors.append({
                "name": f"{m[0]}: {m[1]}",
                "port_hint": m[0], # e.g. "SMB", "LSA Secrets"
                "command": m[2],
                "desc": m[3]
            })

        # Pattern 3: Code Blocks with descriptions
        # Example: - **SSH**: `hydra -L user.txt -P pass.txt -u -V ssh://<IP>`
        code_matches = re.findall(r'-\s*\*\*(.*?)\*\*:\s*`(.*?)`(\s*\(.*?\))?', content)
        for m in code_matches:
            vectors.append({
                "name": f"Method: {m[0]}",
                "port_hint": m[0],
                "command": m[1],
                "desc": m[2] if m[2] else "Targeted execution from training logic."
            })

        return vectors

    def get_suggestions(self, target_data):
        """Matches target ports/OS to training vectors."""
        suggestions = []
        ip = target_data.get("ip", "TARGET")
        open_ports = target_data.get("ports", {}).keys()
        os_info = target_data.get("os", "").lower()
        
        # Keywords to match port_hint to open_ports
        port_map = {
            "22": ["ssh"],
            "445": ["smb", "microsoft-ds", "lsa", "secrets"],
            "88": ["kerberos"],
            "80": ["http", "web"],
            "443": ["https", "ssl", "web"],
            "1433": ["mssql", "sql"],
            "3389": ["rdp"],
            "3306": ["mysql"],
            "2049": ["nfs"]
        }

        for v in self.vectors:
            hint = v["port_hint"].lower()
            matched = False
            
            # Match by Port Number
            if hint in open_ports:
                matched = True
            
            # Match by Service Name
            for port, keywords in port_map.items():
                if port in open_ports and any(k in hint for k in keywords):
                    matched = True
                    break
            
            # Generic/Any Match
            if hint == "any" or "privesc" in hint or "shell" in hint:
                matched = True

            if matched:
                # Clean up command
                cmd = v["command"].replace("<IP>", ip).replace("<TargetIP>", ip).replace("target", ip)
                
                # Check OS compatibility
                is_win_vec = "win" in v["name"].lower() or "win" in v["desc"].lower() or "nxc smb" in cmd
                if is_win_vec and "win" not in os_info and os_info != "":
                    continue

                suggestions.append({
                    "name": v["name"],
                    "command": cmd,
                    "desc": v["desc"]
                })

        # Remove duplicates and return top 8
        unique = []
        seen = set()
        for s in suggestions:
            if s["command"] not in seen:
                unique.append(s)
                seen.add(s["command"])
        
        return unique[:8]
