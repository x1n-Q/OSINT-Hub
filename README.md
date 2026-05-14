# OSINT Hub - All-in-One OSINT Framework

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.8%2B-brightgreen)

> A comprehensive all-in-one OSINT framework with a modern GUI for beginners and powerful CLI for advanced users. Simplifies the use of multiple OSINT tools in one unified platform.

## Features

### For Beginners (No OSINT Experience Needed)
- **One-Click Installation**: Install complex OSINT tools with a single button
- **Simplified Interface**: No need to memorize command-line arguments
- **Guided Workflow**: Step-by-step input forms for each tool
- **All-in-One Results**: Consolidated results viewer with export options
- **Automatic Dependency Handling**: Tools and their dependencies are managed for you

### For Advanced Users
- **Powerful CLI**: Full command-line interface for scripting and automation
- **Batch Processing**: Run multiple tools on multiple targets
- **Custom Parameters**: Access all tool options with a clean interface
- **Export Flexibility**: JSON, CSV, TXT, HTML formats

### Core Capabilities
- **Username Search** across 300+ social networks (Sherlock)
- **Email Intelligence** harvesting and verification
- **Domain & DNS** enumeration and subdomain discovery
- **IP & Geolocation** lookups
- **Social Media** reconnaissance and archiving
- **Phone Number** investigation
- **Image Metadata** extraction
- **Network Scanning** and security auditing
- **Breach Data** checking (HaveIBeenPwned)
- **Dark Web** monitoring tools

## Installation

### Quick Setup

```bash
cd "/home/xinq/OSINT Hub"
python3 -m pip install -r requirements.txt
python3 main.py
```

### Using the Installer

```bash
cd "/home/xinq/OSINT Hub"
python3 setup.py install --user
```

### Dependencies

OSINT Hub requires:
- Python 3.8+
- pip (Python package manager)
- git (for git-based tools)
- Basic build tools (gcc, make)

On Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install python3 python3-pip git build-essential
```

## Usage

### Launch GUI (Beginner-Friendly)

```bash
python3 main.py
```

This opens the modern graphical interface with:
- Tool catalog with icons and descriptions
- Category filtering
- One-click installation
- Interactive parameter forms
- Results viewer and export

### Use CLI (Advanced)

```bash
python3 cli.py --help
```

Common CLI commands:

```bash
# List all tools
python3 cli.py list

# List tools by category
python3 cli.py list --category "Username Search"

# Search for tools
python3 cli.py search username

# Show tool info
python3 cli.py info sherlock

# Install a tool
python3 cli.py install sherlock

# Run a tool
python3 cli.py run sherlock --username target_username

# View results
python3 cli.py results

# Export results
python3 cli.py export --format json --output results.json
```

## How It Works

### 1. Tool Registry
OSINT Hub maintains a curated registry of popular OSINT tools with:
- Automatic detection of installation method
- Simplified parameter mapping
- Usage examples
- Documentation links

### 2. Installation Manager
- Downloads and installs tools automatically
- Handles pip, git, apt, npm, docker installations
- Tracks installed tools
- Manages dependencies

### 3. Unified Runner
Instead of remembering complex commands:

**Without OSINT Hub:**
```bash
sherlock username123 --print --timeout 10 --output all
# Need to remember flags, syntax changes per tool
```

**With OSINT Hub:**
```
GUI: Fill in form fields:
  Username: username123
  [✓] Print output
  Timeout: 10

OR CLI:
python3 cli.py run sherlock --username username123 --print True --timeout 10
```

### 4. Results Management
All scan results are automatically:
- Saved with timestamps
- Categorized by tool
- Searchable and filterable
- Exportable in multiple formats

## Available Tools

| Tool | Purpose | Category |
|------|---------|----------|
| **Sherlock** | Username search across 300+ sites | Social Media |
| **theHarvester** | Email, subdomain, and name scraping | Email Intelligence |
| **SpiderFoot** | Modular OSINT automation | All-in-One |
| **Maltego CE** | Visual link analysis | All-in-One |
| **Recon-ng** | Web reconnaissance framework | All-in-One |
| **Shodan CLI** | Search internet-connected devices | IP & Geolocation |
| **Hunter.io** | Professional email finder | Email Intelligence |
| **HaveIBeenPwned** | Check data breaches | Breach Data |
| **Instaloader** | Download Instagram content | Social Media |
| **Twint** | Twitter scraping without limits | Social Media |
| **GitHub Recon** | GitHub intelligence gathering | Social Media |
| **Amass** | DNS enumeration | Domain & DNS |
| **Nmap** | Network scanning | Network Scanning |
| **ExifTool** | Metadata extraction | Image Metadata |
| **PhoneInfo** | Phone number lookup | Phone Number |
| **Metagoofil** | Document metadata harvesting | Image Metadata |
| **FOCA** | Hidden document information | Image Metadata |
| **SocialScan** | Check username/email availability | Social Media |

*More tools added regularly*

## Directory Structure

```
OSINT Hub/
├── main.py                    # Main launcher (GUI by default)
├── main-gui.py               # GUI-only launcher
├── cli.py                    # CLI interface
├── requirements.txt          # Python dependencies
├── setup.py                  # Installer script
├── README.md                # This file
├── LICENSE                  # License file
├── osinthub/               # Core package
│   ├── __init__.py
│   ├── tools/
│   │   └── registry.py      # Tool definitions
│   ├── core/
│   │   ├── tool_manager.py  # Installation & execution
│   │   ├── results_manager.py  # Results handling
│   │   └── config_manager.py   # Settings management
│   └── gui/
│       └── main_window.py  # GUI application
├── tools/                   # Installed tools directory
├── config/                 # Configuration files
└── output/                 # Default output directory
```

## Configuration

### GUI Settings
Access settings through the GUI:
- Theme (dark/light)
- Accent color
- Results storage location
- Auto-export preferences

### CLI Configuration
Edit `~/.osinthub/config/config.json`:
```json
{
  "theme": "dark",
  "accent_color": "blue",
  "auto_check_updates": true,
  "save_results": true,
  "results_limit": 1000,
  "default_export_format": "json",
  "timeout": 300,
  "max_threads": 3
}
```

## Tips for Beginners

### Getting Started
1. **Launch the app**: `python3 main.py`
2. **Browse tools**: Use the category sidebar
3. **Install a tool**: Click "Install" button on any tool card
4. **Fill the form**: Enter required parameters (the app guides you)
5. **Run it**: Click "Run Tool" and wait for results
6. **View results**: Click "Results" in sidebar

### First Tool to Try
**Sherlock** (username search):
- Install it
- Enter a username (e.g., "john_doe")
- Click Run
- See which social media accounts exist for that username

### Best Practices
- Start with simple tools before complex ones
- Read the tool description before running
- Use the "Examples" section for inspiration
- Check your results in the Results tab
- Export results for reports or sharing

## Tips for Advanced Users

### Scripting with CLI
```bash
# Batch scan multiple usernames
for user in users.txt; do
    python3 cli.py run sherlock --username "$user" >> results.log
done

# Export all results to CSV daily
python3 cli.py export --format csv --output "backup_$(date +%Y%m%d).csv"
```

### Integration with Other Tools
Results are stored in `~/.osinthub/results/` as JSON files. You can:
- Parse them with jq
- Import into Maltego
- Feed into SIEM systems

### Custom Tool Addition
Extend `osinthub/tools/registry.py` to add your own tools:
```python
self._tools["mytool"] = OSINTTool(
    id="mytool",
    name="My Tool",
    description="Description",
    category=ToolCategory.SOCIAL_MEDIA,
    installation_method=InstallationMethod.PIP,
    install_command="pip install mytool",
    run_command="mytool",
    parameters=[...]
)
```

## Troubleshooting

### GUI won't start
```
Error: No module named 'customtkinter'
```
Fix:
```bash
pip install customtkinter
```

### Tool installation fails
Most tools need internet and correct Python version. Check:
```bash
python3 --version  # Should be 3.8+
pip3 --version
```

### Permission denied errors
Some tools require sudo (APT-based). Install them manually:
```bash
sudo apt-get install nmap
sudo apt-get install amass
```

### Results not saving
Check write permissions:
```bash
ls -la ~/.osinthub/
```

## Security & Ethics

**Important**: OSINT Hub is for legitimate intelligence gathering only.
- Only investigate targets you own or have explicit permission to analyze
- Respect privacy and data protection laws
- Never use for harassment, stalking, or illegal activities
- You are responsible for your actions

## Contributing

Contributions welcome! Areas needing help:
- New tool definitions
- GUI improvements
- Documentation
- Bug fixes

## License

MIT License - See LICENSE file for details.

## Support

- **Documentation**: See `docs/` folder (coming soon)
- **Issues**: Report bugs via GitHub Issues
- **Updates**: Auto-check enabled by default

---

**Built for security researchers, investigators, and analysts.**
ult

---

**Built for security researchers, investigators, and analysts.**
