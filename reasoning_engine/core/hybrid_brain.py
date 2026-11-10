import requests
import json
import logging

class HybridBrain:
    def __init__(self, ollama_url="http://127.0.0.1:11434", model="llama3"):
        self.url = f"{ollama_url}/api/generate"
        self.model = model
        self.timeout = 180 # Balanced timeout

    def sanitize_state(self, state):
        """Reduces JSON state to ultra-high-signal text."""
        summary = "TARGETS: "
        for ip, data in state.items():
            summary += f"{ip}[{data.get('access_level', 'None')}], "
        return summary

    def get_chat_response(self, user_query, state_summary, history):
        """Generates a streamlined tactical response."""
        
        # Ultra-Lite Prompt to prevent VRAM overflow
        full_prompt = (
            f"REDOPS Assistant. Target State: {state_summary}. "
            f"Provide a brief, step-by-step PENETRATION TESTING guide for: {user_query}. "
            "No long descriptions. Final answer ONLY."
        )

        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,
                "num_ctx": 2048, # Reduced for memory stability
                "num_predict": 256 # Limit output length
            }
        }

        try:
            response = requests.post(self.url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            return response.json().get("response", "No tactical response generated.")
        except requests.exceptions.HTTPError as e:
            return f"TACTICAL ERROR: Internal Model Failure ({response.status_code}). Simplify your query."
        except Exception as e:
            return f"TACTICAL ERROR: {str(e)}"
