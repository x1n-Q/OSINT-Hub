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

# Bootstrap project virtual environment
echo "Preparing local Python 3.11 virtual environment..."
python3 bootstrap_env.py

# Create symbolic links
echo "Creating command shortcuts..."
chmod +x main.py cli.py menu.py

# Create desktop entry
echo "Creating desktop launcher..."
PROJECT_PATH=$(pwd)
cat > ~/.local/share/applications/osinthub.desktop << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=OSINT Hub
Comment=All-in-One OSINT Framework
Exec=$PROJECT_PATH/.venv/bin/python $PROJECT_PATH/main.py
Icon=$PROJECT_PATH/osinthub/gui/icon.png
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
echo "  2. Run: $PROJECT_PATH/.venv/bin/python $PROJECT_PATH/main.py"
echo "  3. Use CLI: $PROJECT_PATH/.venv/bin/python $PROJECT_PATH/cli.py"
echo ""
echo "Happy hunting! 🔍"
