import sys
import subprocess
import os
import time
from datetime import datetime

# Configuration
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(SCRIPT_DIR, "reasoning_engine/results")
HISTORY_LOG = os.path.join(SCRIPT_DIR, "reasoning_engine/data/history.log")

def run_command(command_args):
    if not command_args:
        print("Usage: pt <command>")
        return

    # Prepare paths
    os.makedirs(RESULTS_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(HISTORY_LOG), exist_ok=True)
    
    # --- INTERNAL REDOPS COMMANDS ---
    # If the user runs 'pt monitor', 'pt clear', etc., we point to main.py
    internal_cmds = ["monitor", "status", "next", "clear", "analyze", "add-user", "add-cred", "add-access", "stuck"]
    if command_args[0] in internal_cmds:
        main_script = os.path.join(SCRIPT_DIR, "reasoning_engine/main.py")
        # Use sys.executable to ensure we use the same venv/interpreter
        full_command = [sys.executable, main_script] + command_args
        subprocess.run(full_command)
        return

    # --- EXTERNAL TOOL WRAPPING ---
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    tool_name = command_args[0].split('/')[-1]
    log_filename = f"{tool_name}_{timestamp}.log"
    log_path = os.path.join(RESULTS_DIR, log_filename)
    
    full_command = " ".join(command_args)
    print(f"\033[94m[*] [PT-Wrapper] Executing: {full_command}\033[0m")
    print(f"\033[94m[*] [PT-Wrapper] Logging to: {log_path}\033[0m\n")

    # Execute and capture
    start_time = time.time()
    try:
        # We use a context manager to open the log file
        with open(log_path, "w") as log_file:
            # Start the process
            process = subprocess.Popen(
                full_command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )

            # Stream output to terminal and file simultaneously
            for line in process.stdout:
                sys.stdout.write(line)
                log_file.write(line)
                sys.stdout.flush()

            process.wait()
            exit_code = process.returncode

    except Exception as e:
        print(f"\033[91m[!] Error executing command: {e}\033[0m")
        exit_code = -1

    duration = round(time.time() - start_time, 2)
    
    # Log to global history
    with open(HISTORY_LOG, "a") as hist:
        hist.write(f"[{datetime.now().isoformat()}] CMD: {full_command} | EXIT: {exit_code} | LOG: {log_filename} | DUR: {duration}s\n")

    if exit_code == 0:
        print(f"\n\033[92m[+] [PT-Wrapper] Command finished successfully (Code 0)\033[0m")
    else:
        print(f"\n\033[91m[!] [PT-Wrapper] Command failed (Code {exit_code})\033[0m")

if __name__ == "__main__":
    run_command(sys.argv[1:])
