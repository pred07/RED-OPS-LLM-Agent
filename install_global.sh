#!/bin/bash
# Pentest Assistant - Global Installer
# Run this inside WSL: chmod +x install_global.sh && ./install_global.sh

PROJECT_DIR=$(pwd)
WRAPPER_PATH="$PROJECT_DIR/pt"

echo "[*] Making 'pt' global from: $PROJECT_DIR"

# Ensure the wrapper is executable
chmod +x "$WRAPPER_PATH"

# Create a symlink in /usr/local/bin
sudo ln -sf "$WRAPPER_PATH" /usr/local/bin/pt

if [ $? -eq 0 ]; then
    echo "[+] SUCCESS: You can now run 'pt <command>' from any terminal!"
else
    echo "[!] FAILED: Could not create symlink. Try running with sudo."
fi
