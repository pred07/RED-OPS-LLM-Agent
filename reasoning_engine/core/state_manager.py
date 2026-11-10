import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional

class StateManager:
    def __init__(self, state_file: str = "reasoning_engine/data/state.json"):
        self.state_file = state_file
        self.state = self._load_state()

    def _get_default_state(self) -> Dict[str, Any]:
        return {
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "project_name": "Pentest Assistant"
            },
            "current_phase": "DISCOVERY",
            "targets": {},
            "pivots": [],
            "tried_actions": [],  # List of unique action identifiers
            "history": []         # Log of all commands and outcomes
        }

    def _load_state(self) -> Dict[str, Any]:
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return self._get_default_state()
        return self._get_default_state()

    def save(self):
        self.state["metadata"]["last_updated"] = datetime.now().isoformat()
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=4)

    # --- Target Management ---

    def update_target(self, ip: str, data: Dict[str, Any]):
        if ip not in self.state["targets"]:
            self.state["targets"][ip] = {
                "ports": {}, # {port_num: {service: "", version: ""}}
                "users": [],
                "creds": [],
                "access_level": None, # None, "user", "admin"
                "vulns": []
            }
        
        # Deep merge/update logic
        target = self.state["targets"][ip]
        if "ports" in data:
            target["ports"].update(data["ports"])
        if "users" in data:
            target["users"] = list(set(target["users"] + data["users"]))
        if "creds" in data:
            # Avoid duplicate creds (e.g., list of dicts)
            for cred in data["creds"]:
                if cred not in target["creds"]:
                    target["creds"].append(cred)
        if "access_level" in data:
            target["access_level"] = data["access_level"]
        
        self.save()

    # --- Phase & Action Tracking ---

    def set_phase(self, phase: str):
        valid_phases = ["DISCOVERY", "ACCESS", "EXPANSION", "DOMINATION"]
        if phase.upper() in valid_phases:
            self.state["current_phase"] = phase.upper()
            self.save()

    def log_action(self, action_id: str, description: str, result: str, success: bool):
        # Add to history
        self.state["history"].append({
            "timestamp": datetime.now().isoformat(),
            "action_id": action_id,
            "description": description,
            "result": result,
            "success": success
        })
        
        # Mark as tried
        if action_id not in self.state["tried_actions"]:
            self.state["tried_actions"].append(action_id)
        
        self.save()

    def is_action_tried(self, action_id: str) -> bool:
        return action_id in self.state["tried_actions"]

    # --- Getters ---

    def get_all_targets(self) -> Dict[str, Any]:
        return self.state["targets"]

    def get_phase(self) -> str:
        return self.state["current_phase"]
