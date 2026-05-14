#!/bin/bash
# OSINT Hub Installation Script
# Usage: bash install.sh

set -e

echo "=================================="
echo "OSINT Hub Installation"
echo "=================================="

# Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed!"
    echo "Install it with: sudo apt-get install python3"
    exit 1
fi

# Check for pip
if ! command -v pip3 &> /dev/null; then
    echo "Installing pip..."
    sudo apt-get update
    sudo apt-get install -y python3-pip
fi

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install -r requirements.txt

# Create symbolic links
echo "Creating command shortcuts..."
chmod +x main.py cli.py menu.py

# Create desktop entry
echo "Creating desktop launcher..."
cat > ~/.local/share/applications/osinthub.desktop << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=OSINT Hub
Comment=All-in-One OSINT Framework
Exec=python3 /home/xinq/OSINT\ Hub/main.py
Icon=osinthub
Terminal=false
Categories=Security;Network;
EOF

# Update desktop database
update-desktop-database ~/.local/share/applications/ 2>/dev/null || true

echo ""
echo "✓ Installation complete!"
echo ""
echo "You can now:"
echo "  1. Launch from Applications menu (OSINT Hub)"
echo "  2. Run: python3 /home/xinq/OSINT\ Hub/main.py"
echo "  3. Use CLI: python3 /home/xinq/OSINT\ Hub/cli.py"
echo ""
echo "Happy hunting! 🔍"
