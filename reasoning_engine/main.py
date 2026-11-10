import yaml
import argparse
import time
import os
import threading
import sys
import select
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text

from core.state_manager import StateManager
from core.decision_engine import DecisionEngine
from core.hybrid_brain import HybridBrain
from core.chat_manager import ChatManager
from core.monitor import Monitor

console = Console()

def get_dashboard_layout(sm: StateManager, cm: ChatManager, thinking: bool = False) -> Layout:
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="main"),
        Layout(name="footer", size=3)
    )
    
    # Header
    layout["header"].update(Panel(
        f"⚡ [bold chartreuse1]REDOPS WAR ROOM[/bold chartreuse1] | [bold cyan]STATE: ACTIVE[/bold cyan] | PHASE: [bold magenta]{sm.get_phase()}[/bold magenta]", 
        border_style="cyan"
    ))
    
    # Main Split
    layout["main"].split_row(
        Layout(name="intel", ratio=1),
        Layout(name="chat", ratio=2)
    )
    
    # --- INTEL MATRIX (LEFT) ---
    targets = sm.get_all_targets()
    intel_table = Table(expand=True, box=None)
    intel_table.add_column("TARGET IP", style="cyan bold")
    intel_table.add_column("ACCESS", style="bold red")
    intel_table.add_column("PORTS", style="magenta")
    
    for ip, data in targets.items():
        access_sym = "💀 ADMIN" if data.get("access_level") == "admin" else "👤 USER" if data.get("access_level") == "user" else "⭕ NONE"
        ports_list = list(data.get("ports", {}).keys())
        ports_str = ", ".join(ports_list[:3]) + ("..." if len(ports_list) > 3 else "")
        intel_table.add_row(ip, access_sym, ports_str or "SCANNING...")
        
    layout["intel"].update(Panel(intel_table, title="[bold cyan]TARGET INTEL MATRIX[/bold cyan]", border_style="cyan"))

    # --- NEURAL CHAT STREAM (RIGHT) ---
    chat_content = Text()
    # Last 8 messages
    for msg in cm.get_last_n(8):
        timestamp = f"[{msg['timestamp']}]"
        sender = f"[{msg['sender']}]"
        if msg['type'] == 'tool':
            chat_content.append(f"{timestamp} {sender} 🛠️ {msg['content']}\n", style="green")
        elif msg['type'] == 'ai':
            chat_content.append(f"{timestamp} {sender} 🧠 {msg['content']}\n", style="deep_pink1")
        else:
            chat_content.append(f"{timestamp} {sender} 👤 {msg['content']}\n", style="cyan")
        chat_content.append("-" * 20 + "\n", style="dim")

    if thinking:
        chat_content.append("REDOPS is thinking...\n", style="italic deep_pink1")

    layout["chat"].update(Panel(
        chat_content,
        title="[bold deep_pink1]NEURAL CHAT STREAM[/bold deep_pink1]",
        border_style="deep_pink1"
    ))
    
    layout["footer"].update(Panel(
        "🟢 [bold green]SENTINEL EYE ACTIVE[/bold green] | [bold cyan]Type query and press Enter[/bold cyan]", 
        border_style="dim"
    ))
    
    return layout

def ai_worker(query, summary, chat_history, hb, cm, status_flag):
    """Background AI response."""
    status_flag[0] = True
    response = hb.get_chat_response(query, summary, chat_history)
    cm.add_message("ai", response, "REDOPS")
    status_flag[0] = False

def main():
    parser = argparse.ArgumentParser(description="REDOPS War Room")
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("monitor")
    subparsers.add_parser("clear")
    args = parser.parse_args()

    # Load Config
    try:
        with open("reasoning_engine/config.yaml", "r") as f:
            config = yaml.safe_load(f)
    except Exception:
        config = {"ollama": {"url": "http://172.30.32.1:11434", "model": "llama3"}}

    sm = StateManager()
    cm = ChatManager()
    hb = HybridBrain(ollama_url=config["ollama"]["url"])
    
    if args.command == "clear":
        cm.clear()
        return

    if args.command == "monitor":
        mon = Monitor(sm, cm)
        threading.Thread(target=mon.start, daemon=True).start()
        
        last_msg_count = len(cm.messages)
        last_state_hash = hash(str(sm.get_all_targets()))
        thinking_status = [False] # Using a list for thread-safe access

        while True:
            sm.state = sm._load_state()
            current_state_hash = hash(str(sm.get_all_targets()))
            
            # --- STABLE REDRAW ---
            # We clear the screen ONLY when something actually changed.
            if len(cm.messages) > last_msg_count or current_state_hash != last_state_hash:
                console.clear()
                console.print(get_dashboard_layout(sm, cm, thinking=thinking_status[0]))
                last_msg_count = len(cm.messages)
                last_state_hash = current_state_hash
            
            # Print the prompt line but don't clear it.
            print(f"\rREDOPS > ", end="", flush=True)
            
            # Wait for input (0.5s timeout)
            rlist, _, _ = select.select([sys.stdin], [], [], 0.5)
            
            if rlist:
                user_input = sys.stdin.readline().strip()
                if user_input:
                    cm.add_message("user", user_input, "Operator")
                    # Force redraw for user message
                    console.clear()
                    console.print(get_dashboard_layout(sm, cm, thinking=True))
                    
                    summary = hb.sanitize_state(sm.get_all_targets())
                    threading.Thread(target=ai_worker, args=(user_input, summary, cm.get_last_n(5), hb, cm, thinking_status), daemon=True).start()
            else:
                # Idle: Auto-AI
                if len(cm.messages) > 0:
                    last_msg = cm.messages[-1]
                    if last_msg['type'] == 'tool' and last_msg_count == len(cm.messages) and not thinking_status[0]:
                        summary = hb.sanitize_state(sm.get_all_targets())
                        threading.Thread(target=ai_worker, args=("Analyze finding.", summary, cm.get_last_n(3), hb, cm, thinking_status), daemon=True).start()
                        last_msg_count = len(cm.messages)
                
                # If we are thinking but the UI isn't showing it yet, redraw once
                if thinking_status[0] and "[italic" not in str(cm.messages[-1].get('content', '')):
                     # This check is just a placeholder, we basically want to redraw when thinking starts/stops
                     pass

if __name__ == "__main__":
    main()
