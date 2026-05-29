# OSINT Hub - All-in-One OSINT Framework

[![PyPI version](https://img.shields.io/pypi/v/osinthub.svg?color=blue)](https://pypi.org/project/osinthub/)
[![Downloads](https://img.shields.io/pypi/dm/osinthub.svg?color=informational&label=downloads%2Fmonth)](https://pypistats.org/packages/osinthub)
[![Python](https://img.shields.io/pypi/pyversions/osinthub.svg?logo=python&logoColor=white)](https://pypi.org/project/osinthub/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

> A unified, beginner-friendly framework for **Open-Source Intelligence (OSINT) research**. Combines a modern GUI and a CLI to simplify common public-data lookups (usernames, domains, IPs, public records) for journalists, researchers, educators, and security professionals.

---

## ⚡ Quick Install (fastest — one command)

```bash
pip install osinthub
```

Then launch:

```bash
osinthub          # GUI (default)
osinthub-cli      # Command-line interface
```

### Even faster, isolated install (recommended)

Use [`pipx`](https://pipx.pypa.io/) to install into its own environment — no dependency conflicts:

```bash
pipx install osinthub
osinthub
```

### Upgrade

```bash
pip install --upgrade osinthub
```

### Available console scripts after install

| Command | Purpose |
|---|---|
| `osinthub` | Launch the GUI |
| `osinthub-cli` | Use the CLI |
| `osinthub-gui` | Same as `osinthub` |
| `osinthub-bootstrap` | Prepare project environment |
| `osinthub-runtime-setup` | Install managed Python runtime for tools |
| `osinthub-audit` | Audit installed OSINT tools |

> 💡 Some bundled research tools are installed on-demand via the app's tool manager. After the first launch, run `osinthub-runtime-setup` once to prepare the Python 3.11 runtime used by those tools.

---

## ⚖️ Legal & Ethical Use

OSINT Hub is designed for **lawful use only** — investigative journalism, academic research, education, brand protection, missing-person searches, due diligence, and authorized security research.

By using this software you agree that:

- ✅ You will only query data that is **publicly available** or that you have **explicit written authorization** to access.
- ✅ You will comply with the **terms of service** of any third-party platform queried, and with all applicable laws in your jurisdiction (including GDPR, CCPA, and similar privacy regulations).
- ❌ You will **not** use this software for stalking, harassment, doxxing, unauthorized access, or any other activity that violates the privacy or rights of others.

The authors and contributors assume **no liability** for misuse. If you are unsure whether a use case is appropriate, **consult a lawyer first**.

---

## Features

### For Beginners (No Prior Experience Needed)
- **One-Click Setup**: Install bundled research tools with a single button
- **Simplified Interface**: No need to memorize command-line arguments
- **Guided Workflow**: Step-by-step input forms for each tool
- **Unified Results View**: Consolidated results viewer with export options
- **Automatic Dependency Handling**: Tool dependencies are managed for you

### For Advanced Users
- **Full CLI**: Command-line interface for scripting and automation
- **Batch Processing**: Run multiple lookups in one go
- **Custom Parameters**: Access all tool options through a clean interface
- **Flexible Export**: JSON, CSV, TXT, HTML formats

### Core Capabilities (Public-Data Lookups)
- **Username Search** across 300+ public social networks (powered by Sherlock)
- **Email Verification** and public-presence lookups
- **Domain & DNS** information and public subdomain discovery
- **IP & Geolocation** lookups using public registries
- **Social Media** public-profile research and archiving
- **Phone Number** carrier and region lookups
- **Image Metadata** (EXIF) extraction from files you own
- **Public Network Info** lookups (WHOIS, ASN, routing)
- **Public Breach Exposure Check** via the official [HaveIBeenPwned](https://haveibeenpwned.com/) API
- **Public-Records Research** helpers

## Manual / Development Installation

> 👉 For most users, **`pip install osinthub`** (above) is the fastest option.
> Use the steps below only if you want to **contribute to the source** or build a Windows `.exe`.

### Development Setup (Python 3.11 + local `.venv`)

```bash
git clone https://github.com/x1n-Q/OSINT-Hub.git
cd OSINT-Hub
python bootstrap_env.py
.venv\Scripts\python.exe main.py
```

On Linux/macOS:

```bash
python3 bootstrap_env.py
.venv/bin/python main.py
```

`bootstrap_env.py` looks for Python `3.11`, creates a project-local virtual environment in `.venv`, installs pinned GUI/runtime dependencies from `requirements-py311.txt`, and installs OSINT Hub into that environment.

### Why This Setup

- Python `3.11` is the most reliable version for the bundled third-party OSINT tools.
- Running from `.venv` avoids "works on my PC" issues caused by global Python packages.
- `main.py`, `cli.py`, and `menu.py` will automatically switch into `.venv` if it already exists.

### Windows Release Build

Use this when your goal is to ship a Windows `.exe` instead of asking users to run the source tree directly.

```bash
python -m pip install -r requirements-build.txt
python build_exe.py --zip
```

If you already created the project `.venv`, you can also use:

```bat
build_release.bat --zip
```

The build creates a release folder in `dist/OSINT-Hub-Windows/` with:
- `OSINT Hub.exe` for the GUI application
- `OSINT Hub Runtime Setup.exe` for preparing the managed Python `3.11` runtime used by tool installers

Important:
- The bundled GUI app is an `.exe`, but many third-party OSINT tools are still Python-based.
- End users should run `OSINT Hub Runtime Setup.exe` once before installing Python-based tools from the app.
- If Python `3.11` is not present on the target PC yet, install it first and then rerun the runtime setup helper.

### Using the Installer

```bash
cd OSINT-Hub
python setup_complete.py
```

### Dependencies

OSINT Hub requires:
- Python 3.11 recommended
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
.venv\Scripts\python.exe main.py
```

This opens the modern graphical interface with:
- Tool catalog with icons and descriptions
- Category filtering
- One-click installation
- Interactive parameter forms
- Results viewer and export

### Use CLI (Advanced)

```bash
.venv\Scripts\python.exe cli.py --help
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

### SocialScan Quick Start

SocialScan is useful for checking whether a username or email is already taken on supported platforms.

Install it:

```bash
python3 cli.py install socialscan
```

Run it for a username:

```bash
python3 cli.py run socialscan danieldepaor
```

Run it for an email:

```bash
python3 cli.py run socialscan danieldepaor@gmail.com
```

In the GUI:
- Open `SocialScan`
- Enter a username or email in the `target` field
- Click `Run Tool`

Notes:
- SocialScan needs working DNS and outbound HTTPS access on the PC running it.
- If every provider returns DNS or connection errors, OSINT Hub now marks the scan as failed instead of showing a false success.
- For the best compatibility, use Python `3.11` through the project `.venv` or the release runtime setup helper.

## Tool Setup and Troubleshooting

This section is the "what do I do when this tool does not install or run?" guide.

### Status Labels in OSINT Hub

- `READY`: Installed and runnable on this machine.
- `AVAILABLE`: OSINT Hub can install it for you.
- `SETUP REQUIRED`: OSINT Hub can use it, but a prerequisite is missing first.
- `MANUAL`: Install it outside OSINT Hub from the official vendor or project docs.
- `DOCS ONLY`: The upstream project is not a real standalone CLI in this build yet.
- `UNSUPPORTED`: The upstream project is too old or incompatible with the managed runtime.

### Before You Install Any Tool

- Prefer Python `3.11`. Many upstream OSINT tools break on Python `3.13+` and especially `3.14`.
- If you are using the Windows `.exe` release, run `OSINT Hub Runtime Setup.exe` once before installing Python-based tools.
- Git-based tools need `git` in your `PATH`.
- Some Windows installs need Microsoft C++ Build Tools because upstream Python packages compile native extensions.
- If a scan fails with `Could not contact DNS servers`, `ClientConnectorDNSError`, or similar network errors, fix DNS/outbound HTTPS first. That is not a bad username or bad install.
- Several tools only accept a specific target type. A person name will not work for domain-only, email-only, network, or file-metadata tools.

### Tool-by-Tool Download Guide

| Tool | Best Install Path | Common Problem | What To Do | Official Docs |
|------|-------------------|----------------|------------|---------------|
| `Sherlock` | Install from OSINT Hub | Username search only | Use a username, not a real name, domain, or file path. If a Git reinstall gets stuck, close Explorer or antivirus tools using the repo folder and retry. | [Sherlock install](https://sherlockproject.xyz/installation) |
| `theHarvester` | Install from OSINT Hub | Domain-only input and source-specific requirements | Use a domain like `example.com`. Some sources need API keys or extra upstream setup, so edit `api-keys.yaml` when needed. | [theHarvester install](https://github.com/laramies/theHarvester/wiki/Installation) |
| `ExifTool` | Windows: official executable is easiest. Source install also works if Perl is installed. | `SETUP REQUIRED` because Perl is missing | On Windows, the easiest path is the official ExifTool package. If you want the Git/source install, install Perl first and then retry from OSINT Hub. Use a file or directory target, not a username. | [ExifTool install](https://exiftool.org/install.html) |
| `SocialScan` | Install from OSINT Hub | DNS or HTTPS connection failures | Use a username or email address only. If every provider shows DNS/connect errors, fix the PC network first and retry. | [SocialScan README](https://github.com/iojw/socialscan) |
| `Nmap` | Manual install from the official installer or OS package manager | Not auto-installed by OSINT Hub | Install Nmap manually. On Windows, install from the official site and keep the packet capture components if prompted. Use a host or IP target, not a person or email. | [Nmap download](https://nmap.org/download.html) |
| `Amass` | Manual install from release, package manager, or Docker | Not auto-installed and domain-only | Install a release build or use your package manager. Use `amass enum -d example.com` style targets. Many richer data sources work better once you configure provider keys. | [Amass docs](https://owasp-amass.github.io/docs/) |
| `PhoneInfo` / `PhoneInfoga` | Manual install from the official binary, Homebrew, or Docker | Not a pip tool and phone format matters | Follow the official install page. Use a full international number like `+15551234567`. | [PhoneInfoga install](https://sundowndev.github.io/phoneinfoga/getting-started/install/) |
| `SpiderFoot` | Install from OSINT Hub or use Docker | Windows installs can fail on `lxml` / native build steps | If you see `Microsoft Visual C++ 14.0 or greater is required`, install Microsoft C++ Build Tools and retry. If you want fewer Python dependency problems, use the Docker path from the upstream docs instead. | [SpiderFoot docs](https://www.spiderfoot.net/documentation/) |
| `Maltego CE` | Manual vendor install | GUI app with account/login flow | Download it from Maltego, install it manually, and sign in. OSINT Hub links it but does not bundle the installer. | [Maltego docs](https://docs.maltego.com/) |
| `Recon-ng` | Install from OSINT Hub | Framework modules can still need their own setup | The core framework installs cleanly, but many marketplace modules need API keys or extra dependencies. Use `marketplace info <module>` inside Recon-ng when a module does not run. | [Recon-ng getting started](https://github.com/lanmaster53/recon-ng/wiki/Getting-Started) |
| `Shodan CLI` | Install from OSINT Hub | API key not initialized or Python runtime mismatch | After install, run `shodan init YOUR_API_KEY`. If startup fails with `pkg_resources` or similar packaging errors, reinstall it inside the Python `3.11` runtime instead of a newer global Python. | [Shodan CLI getting started](https://help.shodan.io/command-line-interface/1-getting-started) |
| `Hunter.io` | Docs only for now | No bundled standalone CLI | Hunter is API-first. Create a Hunter account, get an API key, and use the official API endpoints in your own wrapper or future OSINT Hub integration. | [Hunter API docs](https://hunter.io/api-documentation/) |
| `HaveIBeenPwned` / `h8mail` | Install from OSINT Hub | Wrong target type | This tool expects an email address, not a person name or username. Some extra breach sources also need their own API keys or config entries. | [h8mail project](https://github.com/khast3x/h8mail) |
| `Instaloader` | Install from OSINT Hub | Login/session issues and rate limits | Use an Instagram profile or supported Instagram target. If anonymous scraping is limited, use `--login` and keep the saved session file. If you hit `429` or rate-limit messages, wait and reuse the same session. | [Instaloader install](https://instaloader.github.io/installation.html) |
| `Twint` | Install from OSINT Hub if it works, otherwise treat as experimental | Old dependency stack and Windows build failures | In this project, Windows installs may fail while building native dependencies such as `cchardet`. Prefer Python `3.11`, and be prepared to use a separate manual or Docker-based setup if upstream pip installs fail. | [Twint setup](https://github.com/twintproject/twint/wiki/Setup) |
| `GitHub Recon` / `github-dorks` | Install from OSINT Hub | Old dependency stack and missing GitHub authentication | If the tool throws import errors on a very new Python, move back to the managed Python `3.11` runtime. For better results and fewer rate-limit problems, provide GitHub authentication when using the upstream tool. | [GitHub Dorks repo](https://github.com/techgaun/github-dorks) |
| `Metagoofil` | Do not rely on the bundled runtime | Legacy Python 2 code | This upstream project is legacy and is marked `UNSUPPORTED` in OSINT Hub because it does not run on the managed Python 3 runtime. Use another metadata workflow such as ExifTool or FOCA, or isolate Metagoofil in a legacy lab/VM if you absolutely need it. | [Metagoofil repo](https://github.com/laramies/metagoofil) |
| `FOCA` | Manual install on Windows | Windows-only GUI workflow | Download FOCA from its official project page and run it manually on Windows. It is not bundled as a Python tool inside OSINT Hub. | [FOCA repo](https://github.com/ElevenPaths/FOCA) |

### Fast "Wrong Target" Checks

If a tool installs fine but still "does nothing", check the target type first:

- Use `Sherlock`, `SocialScan`, `Instaloader`, or `GitHub Recon` for usernames or social targets.
- Use `theHarvester` or `Amass` for domains.
- Use `Nmap` for IPs or hostnames.
- Use `ExifTool` or `FOCA` for files, directories, or document metadata workflows.
- Use `PhoneInfoga` for full phone numbers with country codes.
- Use `h8mail` for email addresses.

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

```text
OSINT Hub/
|-- main.py                    # Main launcher (GUI by default)
|-- main-gui.py                # GUI-only launcher
|-- cli.py                     # CLI interface
|-- requirements.txt           # Python dependencies
|-- setup.py                   # Installer script
|-- README.md                  # This file
|-- LICENSE                    # License file
|-- osinthub/                  # Core package
|   |-- __init__.py
|   |-- tools/
|   |   `-- registry.py        # Tool definitions
|   |-- core/
|   |   |-- tool_manager.py    # Installation and execution
|   |   |-- results_manager.py # Results handling
|   |   `-- config_manager.py  # Settings management
|   `-- gui/
|       `-- main_window.py     # GUI application
|-- tools/                     # Installed tools directory
|-- config/                    # Configuration files
`-- output/                    # Default output directory
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

### SocialScan shows DNS or connection errors
Example errors:
```text
ClientConnectorDNSError
Could not contact DNS servers
Cannot connect to host ...:443
```

What this means:
- OSINT Hub started SocialScan correctly, but the PC could not reach the target sites.
- This is usually a local DNS, firewall, proxy, VPN, antivirus, or outbound network restriction issue.

What to check on Windows:
```powershell
nslookup github.com
Test-NetConnection github.com -Port 443
```

If these fail:
- Fix the PC network or DNS settings first
- Retry SocialScan after confirming the machine can resolve domains and reach HTTPS sites
- If you are on a restricted network, try another DNS server or another connection

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

## Credits & Attributions

OSINT Hub is a framework that integrates and simplifies the use of many incredible open-source tools. We would like to thank the authors and contributors of the following projects:

| Tool | Category | Original Repository / Homepage |
|------|----------|-------------------------------|
| **Sherlock** | Username Search | [sherlock-project/sherlock](https://github.com/sherlock-project/sherlock) |
| **theHarvester** | Email Intelligence | [laramies/theHarvester](https://github.com/laramies/theHarvester) |
| **SpiderFoot** | All-in-One | [smicallef/spiderfoot](https://github.com/smicallef/spiderfoot) |
| **Maltego** | All-in-One | [Maltego Technologies](https://www.maltego.com/) |
| **Recon-ng** | All-in-One | [lanmaster53/recon-ng](https://github.com/lanmaster53/recon-ng) |
| **Shodan CLI** | IP & Geolocation | [achillean/shodan-python](https://github.com/achillean/shodan-python) |
| **Hunter.io** | Email Intelligence | [Hunter.io](https://hunter.io/) |
| **HaveIBeenPwned** | Breach Data | [Troy Hunt (HIBP)](https://haveibeenpwned.com/) |
| **Instaloader** | Social Media | [instaloader/instaloader](https://github.com/instaloader/instaloader) |
| **Twint** | Social Media | [twintproject/twint](https://github.com/twintproject/twint) |
| **GitHub Recon** | Social Media | [techgaun/github-dorks](https://github.com/techgaun/github-dorks) |
| **PhoneInfoga** | Phone Number | [sundowndev/phoneinfoga](https://github.com/sundowndev/phoneinfoga) |
| **ExifTool** | Image Metadata | [Phil Harvey (ExifTool)](https://exiftool.org/) |
| **Amass** | Domain & DNS | [owasp-amass/amass](https://github.com/owasp-amass/amass) |
| **Nmap** | Network Scanning | [Gordon Lyon (Nmap)](https://nmap.org/) |
| **Metagoofil** | Image Metadata | [laramies/metagoofil](https://github.com/laramies/metagoofil) |
| **SocialScan** | Social Media | [iojw/socialscan](https://github.com/iojw/socialscan) |
| **EmailHarvester** | Email Intelligence | [maldevel/EmailHarvester](https://github.com/maldevel/EmailHarvester) |
| **Social ID Extractor** | Social Media | [soxoj/socid-extractor](https://github.com/soxoj/socid-extractor) |

Please support these projects by visiting their repositories, giving them a star, or contributing to their development.

## Author

**Daniel Depaor** ([@x1n-Q](https://github.com/x1n-Q))

## License

MIT License - See [LICENSE](LICENSE) file for details.

## Support

- **Documentation**: See `docs/` folder (coming soon)
- **Issues**: Report bugs via GitHub Issues
- **Updates**: Auto-check enabled by default

---

**Built for security researchers, investigators, and analysts.**
