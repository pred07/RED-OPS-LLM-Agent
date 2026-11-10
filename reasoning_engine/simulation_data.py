import json
import os
from datetime import datetime

STATE_FILE = "reasoning_engine/data/state.json"
CHAT_FILE = "reasoning_engine/data/chat_history.json"

def populate():
    # Correct Nested Structure
    state = {
        "metadata": {
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "project_name": "Pentest Assistant"
        },
        "current_phase": "DISCOVERY",
        "targets": {
            "10.10.10.15": {
                "hostname": "prod-db-01.corp.local",
                "os": "Windows Server 2019",
                "access_level": "none",
                "ports": {
                    "1433": {"service": "ms-sql-s", "version": "2019", "state": "open"},
                    "445": {"service": "microsoft-ds", "version": "", "state": "open"}
                },
                "users": [],
                "creds": []
            },
            "10.10.10.20": {
                "hostname": "mail-gw.corp.local",
                "os": "Ubuntu 22.04",
                "access_level": "none",
                "ports": {
                    "25": {"service": "smtp", "version": "Postfix", "state": "open"},
                    "80": {"service": "http", "version": "Apache", "state": "open"},
                    "443": {"service": "https", "version": "Apache", "state": "open"}
                },
                "users": ["admin", "support"],
                "creds": []
            },
            "10.10.10.5": {
                "hostname": "dc-01.corp.local",
                "os": "Windows Server 2022",
                "access_level": "admin",
                "ports": {
                    "88": {"service": "kerberos", "version": "", "state": "open"},
                    "389": {"service": "ldap", "version": "", "state": "open"},
                    "445": {"service": "microsoft-ds", "version": "", "state": "open"}
                },
                "users": ["Administrator", "svc_backup"],
                "creds": ["Administrator:P@ssw0rd123"]
            },
            "192.168.1.50": {
                "hostname": "workstation-hr",
                "os": "Windows 10",
                "access_level": "user",
                "ports": {
                    "3389": {"service": "ms-wbt-server", "version": "", "state": "open"}
                },
                "users": ["j.doe"],
                "creds": []
            }
        },
        "pivots": [],
        "tried_actions": [],
        "history": []
    }

    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=4)

    # 2. Rich Chat History
    chat = [
        {"type": "ai", "content": "War Room Initialized. Sentinel Eye is monitoring for tool logs.", "sender": "REDOPS", "timestamp": "15:00:01"},
        {"type": "tool", "content": "Nmap scan completed for 10.10.10.0/24. Found 4 active hosts.", "sender": "Nmap", "timestamp": "15:05:20"},
        {"type": "ai", "content": "Analyzing scan results. Target 10.10.10.5 (DC-01) is a high-value Kerberos target. I recommend Module 3: Active Directory Enumeration.", "sender": "REDOPS", "timestamp": "15:05:25"},
        {"type": "user", "content": "Check for SMB signing on the database server.", "sender": "Operator", "timestamp": "15:10:00"},
        {"type": "tool", "content": "NetExec: 10.10.10.15 - SMB signing is DISABLED.", "sender": "NetExec", "timestamp": "15:10:15"},
        {"type": "ai", "content": "**STRATEGY ALERT**: SMB Signing is disabled on the production database. This is a critical finding. I suggest an SMB Relay attack to capture administrator hashes.", "sender": "REDOPS", "timestamp": "15:10:20"},
        {"type": "user", "content": "What about the mail gateway?", "sender": "Operator", "timestamp": "15:15:00"},
        {"type": "ai", "content": "Mail gateway (10.10.10.20) is running an older version of Apache. I am cross-referencing for known CVEs. Stay tuned.", "sender": "REDOPS", "timestamp": "15:15:05"},
        {"type": "tool", "content": "Kerbrute: Found valid user 'j.doe' on 192.168.1.50.", "sender": "Kerbrute", "timestamp": "15:20:00"},
        {"type": "ai", "content": "User 'j.doe' discovered. This provides a potential lateral movement path from the HR workstation to the internal network.", "sender": "REDOPS", "timestamp": "15:20:10"}
    ]

    with open(CHAT_FILE, "w") as f:
        json.dump(chat, f, indent=4)

    print("Successfully injected simulation data with correct architecture.")

if __name__ == "__main__":
    populate()
