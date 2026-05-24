"""
Tool Registry
Defines the registry of available OSINT tools and their parameters.
"""

from enum import Enum
from typing import List, Optional

class ToolCategory(Enum):
    ALL_IN_ONE = "All-in-One"
    EMAIL_INTEL = "Email Intelligence"
    USERNAME_SEARCH = "Username Search"
    SOCIAL_MEDIA = "Social Media"
    IP_GEOLOCATION = "IP & Geolocation"
    DOMAIN_DNS = "Domain & DNS"
    NETWORK_SCANNING = "Network Scanning"
    IMAGE_METADATA = "Image Metadata"
    PHONE_NUMBER = "Phone Number"
    BREACH_DATA = "Breach Data"

class InstallationMethod(Enum):
    PIP = "pip"
    GIT = "git"
    APT = "apt"
    NPM = "npm"
    CUSTOM = "custom"
    DOCKER = "docker"

class Parameter:
    """Defines a tool parameter."""
    def __init__(self, name: str, flag: Optional[str] = None, default: Optional[str] = None, 
                 description: str = "", required: bool = False, type: str = "string", 
                 options: Optional[List[str]] = None):
        self.name = name
        self.flag = flag
        self.default = default
        self.description = description
        self.required = required
        self.type = type
        self.options = options

class OSINTTool:
    """Defines an OSINT tool."""
    def __init__(self, id: str, name: str, description: str, category: ToolCategory, 
                 installation_method: InstallationMethod, install_command: str, run_command: str, 
                 parameters: Optional[List[Parameter]] = None, homepage: str = "", 
                 documentation: str = "", examples: Optional[List[str]] = None, 
                 icon: str = "🛠️", long_description: Optional[str] = None,
                 supported_platforms: Optional[List[str]] = None, availability_note: str = "",
                 healthcheck_args: Optional[List[str]] = None,
                 minimum_python: Optional[tuple[int, int]] = None,
                 maximum_python: Optional[tuple[int, int]] = None,
                 required_commands: Optional[List[str]] = None):
        self.id = id
        self.name = name
        self.description = description
        self.long_description = long_description
        self.category = category
        self.installation_method = installation_method
        self.install_command = install_command
        self.run_command = run_command
        self.parameters = parameters or []
        self.homepage = homepage
        self.documentation = documentation
        self.examples = examples or []
        self.icon = icon
        self.supported_platforms = [platform.lower() for platform in supported_platforms] if supported_platforms else []
        self.availability_note = availability_note
        self.healthcheck_args = healthcheck_args or []
        self.minimum_python = minimum_python
        self.maximum_python = maximum_python
        self.required_commands = required_commands or []
        
        # State variables loaded dynamically
        self.installed = False
        self.install_path = ""

class ToolRegistry:
    """Registry of all supported OSINT tools."""
    def __init__(self):
        self._tools = {}
        self._register_default_tools()

    def _register_default_tools(self):
        # 1. Sherlock
        self._tools["sherlock"] = OSINTTool(
            id="sherlock",
            name="Sherlock",
            description="Hunt down social media accounts by username across 300+ sites.",
            long_description="Sherlock allows you to search for a single username across a vast number of social media and web platforms. It is incredibly useful for finding the digital footprint of a target across the web.",
            category=ToolCategory.USERNAME_SEARCH,
            installation_method=InstallationMethod.GIT,
            install_command="git clone https://github.com/sherlock-project/sherlock.git",
            run_command="python3 -m sherlock_project",  # tool_manager.py handles Python script invocation and checks install_path
            parameters=[
                Parameter(name="username", flag=None, required=True, description="Username to search for"),
                Parameter(name="timeout", flag="--timeout", default="60", description="Time to wait for responses in seconds"),
                Parameter(name="print", flag="--print", default="False", type="boolean", description="Print all results (even if username not found)")
            ],
            homepage="https://github.com/sherlock-project/sherlock",
            documentation="https://github.com/sherlock-project/sherlock/blob/master/README.md",
            examples=["sherlock target_user", "sherlock target_user --timeout 10"],
            icon="🔎"
        )

        # 2. theHarvester
        self._tools["harvester"] = OSINTTool(
            id="harvester",
            name="theHarvester",
            description="Gather subdomains, email addresses, open ports and employee names from public sources.",
            long_description="theHarvester is a tool for gathering subdomain names, e-mail addresses, virtual hosts, open ports/ banners, and employee names from different public sources (search engines, pgp key servers and SHODAN database).",
            category=ToolCategory.EMAIL_INTEL,
            installation_method=InstallationMethod.GIT,
            install_command="git clone https://github.com/laramies/theHarvester.git",
            run_command="python3 bin/theHarvester",
            parameters=[
                Parameter(name="domain", flag="-d", required=True, description="Domain to search"),
                Parameter(name="limit", flag="-l", default="500", description="Limit the number of search results"),
                Parameter(name="source", flag="-b", default="duckduckgo", description="Data source (e.g. duckduckgo, yahoo, crtsh, all)")
            ],
            homepage="https://github.com/laramies/theHarvester",
            documentation="https://github.com/laramies/theHarvester/blob/master/README.md",
            examples=["theHarvester -d targetcompany.com -b bing", "theHarvester -d targetcompany.com -l 100 -b all"],
            icon="📧"
        )

        # 3. ExifTool
        self._tools["exiftool"] = OSINTTool(
            id="exiftool",
            name="ExifTool",
            description="Read, write and edit meta information in a wide variety of files.",
            long_description="ExifTool is a platform-independent Perl library plus a command-line application for reading, writing and editing meta information in a wide variety of files. It supports EXIF, GPS, IPTC, XMP, JFIF, GeoTIFF, ICC Profile, Photoshop IRB, FlashPix, AFCP and ID3, as well as the maker notes of many digital cameras.",
            category=ToolCategory.IMAGE_METADATA,
            installation_method=InstallationMethod.GIT,
            install_command="git clone https://github.com/exiftool/exiftool.git",
            run_command="perl exiftool",
            parameters=[
                Parameter(name="target", flag=None, required=True, description="Path to image file or directory")
            ],
            homepage="https://exiftool.org/",
            documentation="https://exiftool.org/faq.html",
            examples=["exiftool path/to/image.jpg", "exiftool path/to/directory"],
            icon="🖼️",
            supported_platforms=["windows", "linux", "macos"],
            availability_note="Official GitHub source install requires Perl. On Windows without Perl, use the official ExifTool executable package from exiftool.org instead.",
            healthcheck_args=["-ver"],
            required_commands=["perl"]
        )

        # 4. SocialScan
        self._tools["socialscan"] = OSINTTool(
            id="socialscan",
            name="SocialScan",
            description="Check email address and username availability on popular platforms.",
            long_description="socialscan offers accurate and fast queries to check username and email address availability on a range of online platforms, bypassing rate-limiting and IP blocking.",
            category=ToolCategory.SOCIAL_MEDIA,
            installation_method=InstallationMethod.PIP,
            install_command="pip install socialscan",
            run_command="socialscan",
            parameters=[
                Parameter(name="target", flag=None, required=True, description="Username or email to check")
            ],
            homepage="https://github.com/iojw/socialscan",
            documentation="https://github.com/iojw/socialscan/blob/master/README.md",
            examples=["socialscan username123", "socialscan email@domain.com"],
            icon="🔍"
        )

        # 5. Nmap
        self._tools["nmap"] = OSINTTool(
            id="nmap",
            name="Nmap",
            description="Network exploration tool and security / port scanner.",
            long_description="Nmap ('Network Mapper') is a free and open source utility for network discovery and security auditing. Many systems and network administrators also find it useful for tasks such as network inventory, managing service upgrade schedules, and monitoring host or service uptime.",
            category=ToolCategory.NETWORK_SCANNING,
            installation_method=InstallationMethod.CUSTOM,
            install_command="sudo apt-get install nmap",
            run_command="nmap",
            parameters=[
                Parameter(name="target", flag=None, required=True, description="Target IP or hostname"),
                Parameter(name="scan_type", flag="-sS", default="", description="Perform a TCP SYN scan"),
                Parameter(name="ports", flag="-p", default="", description="Ports to scan (e.g. 80,443)")
            ],
            homepage="https://nmap.org/",
            documentation="https://nmap.org/book/man.html",
            examples=["nmap scanme.nmap.org", "nmap -p 80,443 target_ip"],
            icon="🌐",
            supported_platforms=["windows", "linux", "macos"],
            availability_note="Manual install required. Install Nmap from the official installer or your OS package manager."
        )

        # 6. Amass
        self._tools["amass"] = OSINTTool(
            id="amass",
            name="Amass",
            description="In-depth DNS enumeration and network mapping.",
            long_description="The OWASP Amass Project performs in-depth scaffolding of open-source intelligence gathering and active reconnaissance techniques on domain names and IP addresses.",
            category=ToolCategory.DOMAIN_DNS,
            installation_method=InstallationMethod.CUSTOM,
            install_command="sudo apt-get install amass",
            run_command="amass enum",
            parameters=[
                Parameter(name="domain", flag="-d", required=True, description="Domain to enumerate")
            ],
            homepage="https://github.com/owasp-amass/amass",
            documentation="https://github.com/owasp-amass/amass/blob/master/doc/user_guide.md",
            examples=["amass enum -d example.com"],
            icon="🛡️",
            supported_platforms=["windows", "linux", "macos"],
            availability_note="Manual install required. Install an Amass release or package for your OS."
        )

        # 7. PhoneInfo
        self._tools["phoneinfo"] = OSINTTool(
            id="phoneinfo",
            name="PhoneInfo",
            description="Phone number information gathering framework.",
            long_description="An information gathering tool for phone numbers. It checks for carrier info, location, and potential leaks associated with the number.",
            category=ToolCategory.PHONE_NUMBER,
            installation_method=InstallationMethod.CUSTOM,
            install_command="Install PhoneInfoga from its official binary, Homebrew, or Docker instructions",
            run_command="phoneinfoga scan",
            parameters=[
                Parameter(name="number", flag="-n", required=True, description="Phone number with country code (e.g. +1234567890)")
            ],
            homepage="https://github.com/sundowndev/phoneinfoga",
            documentation="https://sundowndev.github.io/phoneinfoga/",
            examples=["phoneinfoga scan -n +1234567890"],
            icon="📞",
            supported_platforms=["windows", "linux", "macos"],
            availability_note="Manual install required. PhoneInfoga is distributed as an official binary, Homebrew package, or Docker image."
        )

        # 8. SpiderFoot
        self._tools["spiderfoot"] = OSINTTool(
            id="spiderfoot",
            name="SpiderFoot",
            description="Modular OSINT automation engine for intelligence gathering.",
            long_description="SpiderFoot is an open source intelligence (OSINT) automation tool. It integrates with over 100 public data sources to gather intelligence on IP addresses, domain names, e-mail addresses, names and more.",
            category=ToolCategory.ALL_IN_ONE,
            installation_method=InstallationMethod.GIT,
            install_command="git clone https://github.com/smicallef/spiderfoot.git",
            run_command="python3 sf.py",
            parameters=[
                Parameter(name="target", flag="-s", required=True, description="Target domain, IP, or email"),
                Parameter(name="port", flag="-p", default="5001", description="Port for web interface")
            ],
            homepage="https://www.spiderfoot.net/",
            documentation="https://www.spiderfoot.net/documentation/",
            examples=["spiderfoot -s example.com", "spiderfoot -p 5001"],
            icon="🕷️"
        )

        # 9. Maltego CE
        self._tools["maltego"] = OSINTTool(
            id="maltego",
            name="Maltego CE",
            description="Visual link analysis tool for gathering and connecting information.",
            long_description="Maltego is an interactive data mining tool that renders directed graphs for link analysis. The tool is used in online investigation for finding relationships between pieces of information from various sources on the Internet.",
            category=ToolCategory.ALL_IN_ONE,
            installation_method=InstallationMethod.CUSTOM,
            install_command="Download and install from maltego.com",
            run_command="maltego",
            parameters=[],
            homepage="https://www.maltego.com/",
            documentation="https://docs.maltego.com/",
            examples=["maltego"],
            icon="🌿",
            supported_platforms=["windows", "linux", "macos"],
            availability_note="Manual install required. Download Maltego from the vendor site."
        )

        # 10. Recon-ng
        self._tools["reconng"] = OSINTTool(
            id="reconng",
            name="Recon-ng",
            description="Web reconnaissance framework written in Python.",
            long_description="Recon-ng is a full-featured Web Reconnaissance framework written in Python. Complete with independent modules, database interaction, built in convenience functions, interactive help, and command completion, Recon-ng provides a powerful environment in which open source web-based reconnaissance can be conducted quickly and thoroughly.",
            category=ToolCategory.ALL_IN_ONE,
            installation_method=InstallationMethod.GIT,
            install_command="git clone https://github.com/lanmaster53/recon-ng.git",
            run_command="python3 recon-ng",
            parameters=[
                Parameter(name="workspace", flag="-w", description="Workspace name")
            ],
            homepage="https://github.com/lanmaster53/recon-ng",
            documentation="https://github.com/lanmaster53/recon-ng/wiki",
            examples=["recon-ng", "recon-ng -w my_workspace"],
            icon="⚔️"
        )

        # 11. Shodan CLI
        self._tools["shodan"] = OSINTTool(
            id="shodan",
            name="Shodan CLI",
            description="Search internet-connected devices using Shodan.",
            long_description="Shodan is a search engine for Internet-connected devices. The Shodan Command Line Interface (CLI) allows you to search Shodan, get host information, download data, and more from the comfort of your terminal.",
            category=ToolCategory.IP_GEOLOCATION,
            installation_method=InstallationMethod.PIP,
            install_command="pip install setuptools shodan",
            run_command="shodan",
            parameters=[
                Parameter(name="query", flag="search", required=True, description="Search query")
            ],
            homepage="https://github.com/achillean/shodan-python",
            documentation="https://cli.shodan.io/",
            examples=["shodan search apache", "shodan host 8.8.8.8"],
            icon="📡",
            healthcheck_args=["--help"]
        )

        # 12. Hunter.io
        self._tools["hunter"] = OSINTTool(
            id="hunter",
            name="Hunter.io",
            description="Hunter.io API helper (manual integration required).",
            long_description="Hunter.io lets you find professional email addresses in seconds and connect with the people that matter for your business. The bundled pyhunter package is a Python library rather than a ready-to-run CLI, so this entry is currently documentation-only until a native OSINT Hub wrapper is added.",
            category=ToolCategory.EMAIL_INTEL,
            installation_method=InstallationMethod.CUSTOM,
            install_command="Create a Hunter.io API integration script with your API key; pyhunter does not ship a standalone CLI",
            run_command="",
            parameters=[
                Parameter(name="domain", flag="-d", required=True, description="Domain to search")
            ],
            homepage="https://hunter.io/",
            documentation="https://github.com/fnandoconrad/pyhunter",
            examples=[],
            icon="🎯",
            supported_platforms=["windows", "linux", "macos"],
            availability_note="Docs only for now. The upstream pyhunter package is a Python library, not a standalone CLI."
        )

        # 13. HaveIBeenPwned
        self._tools["hibp"] = OSINTTool(
            id="hibp",
            name="HaveIBeenPwned",
            description="Check if emails have been compromised in data breaches.",
            long_description="Using h8mail, this tool allows you to check HaveIBeenPwned and other databases to see if email addresses have been compromised in public data breaches.",
            category=ToolCategory.BREACH_DATA,
            installation_method=InstallationMethod.PIP,
            install_command="pip install h8mail",
            run_command="h8mail",
            parameters=[
                Parameter(name="target", flag="-t", required=True, description="Email address to check")
            ],
            homepage="https://haveibeenpwned.com/",
            documentation="https://github.com/khast33/h8mail",
            examples=["h8mail -t email@domain.com"],
            icon="🔓"
        )

        # 14. Instaloader
        self._tools["instaloader"] = OSINTTool(
            id="instaloader",
            name="Instaloader",
            description="Download pictures, videos and metadata from Instagram.",
            long_description="Instaloader is a tool to download photos, videos, and metadata from Instagram profiles, hashtags, and stories. It handles login, rates, and can archive complete profiles.",
            category=ToolCategory.SOCIAL_MEDIA,
            installation_method=InstallationMethod.PIP,
            install_command="pip install instaloader",
            run_command="instaloader",
            parameters=[
                Parameter(name="profile", flag=None, required=True, description="Instagram profile name")
            ],
            homepage="https://instaloader.github.io/",
            documentation="https://instaloader.github.io/cli-options.html",
            examples=["instaloader profile_name"],
            icon="📸"
        )

        # 15. Twint
        self._tools["twint"] = OSINTTool(
            id="twint",
            name="Twint",
            description="Advanced Twitter scraping tool written in Python.",
            long_description="Twint is an advanced Twitter scraping tool written in Python that allows for scraping Tweets from Twitter profiles without using Twitter's API.",
            category=ToolCategory.SOCIAL_MEDIA,
            installation_method=InstallationMethod.PIP,
            install_command="pip install twint",
            run_command="twint",
            parameters=[
                Parameter(name="username", flag="-u", required=True, description="Twitter username to scrape")
            ],
            homepage="https://github.com/twintproject/twint",
            documentation="https://github.com/twintproject/twint/wiki",
            examples=["twint -u target_user"],
            icon="🐦"
        )

        # 16. GitHub Recon
        self._tools["githubrecon"] = OSINTTool(
            id="githubrecon",
            name="GitHub Recon",
            description="Search GitHub repositories for sensitive data and secrets.",
            long_description="Uses github-dorks to search public GitHub repositories for leaked credentials, private keys, and sensitive data.",
            category=ToolCategory.SOCIAL_MEDIA,
            installation_method=InstallationMethod.GIT,
            install_command="git clone https://github.com/techgaun/github-dorks.git",
            run_command="python3 github-dork.py",
            parameters=[
                Parameter(name="target", flag="-u", required=True, description="GitHub user or organization")
            ],
            homepage="https://github.com/techgaun/github-dorks",
            documentation="https://github.com/techgaun/github-dorks/blob/master/README.md",
            examples=["github-dork.py -u target_user"],
            icon="🐙"
        )

        # 17. Metagoofil
        self._tools["metagoofil"] = OSINTTool(
            id="metagoofil",
            name="Metagoofil",
            description="Information gathering tool for extracting document metadata.",
            long_description="Metagoofil is an information gathering tool designed for extracting metadata of public documents (pdf, doc, xls, ppt, docx, xlsx, pptx) belonging to a target company.",
            category=ToolCategory.IMAGE_METADATA,
            installation_method=InstallationMethod.GIT,
            install_command="git clone https://github.com/laramies/metagoofil.git",
            run_command="python3 metagoofil.py",
            parameters=[
                Parameter(name="domain", flag="-d", required=True, description="Domain to search"),
                Parameter(name="file_type", flag="-t", default="pdf,doc,xls", description="File types to download")
            ],
            homepage="https://github.com/laramies/metagoofil",
            documentation="https://github.com/laramies/metagoofil/blob/master/README.md",
            examples=["metagoofil -d example.com -t pdf"],
            icon="📁",
            availability_note="Legacy upstream project. The bundled script is Python 2 code and does not run on the managed Python 3 runtime.",
            healthcheck_args=["-h"],
            maximum_python=(2, 7)
        )

        # 18. FOCA
        self._tools["foca"] = OSINTTool(
            id="foca",
            name="FOCA",
            description="Tool to find metadata and hidden information in documents.",
            long_description="FOCA (Fingerprinting Organizations with Collected Archives) is a tool used mainly to find metadata and hidden information in the documents it scans.",
            category=ToolCategory.IMAGE_METADATA,
            installation_method=InstallationMethod.CUSTOM,
            install_command="Download and run on Windows from ElevenPaths GitHub",
            run_command="FOCA.exe",
            parameters=[
                Parameter(name="target", flag=None, required=False, description="Domain or document directory to analyze")
            ],
            homepage="https://github.com/ElevenPaths/FOCA",
            documentation="https://github.com/ElevenPaths/FOCA/blob/master/README.md",
            examples=["FOCA.exe"],
            icon="🦊",
            supported_platforms=["windows"],
            availability_note="Windows only. Install FOCA manually from its upstream release."
        )

    def get_tool(self, tool_id: str) -> Optional[OSINTTool]:
        return self._tools.get(tool_id.lower())

    def get_all_tools(self) -> List[OSINTTool]:
        return list(self._tools.values())

    def get_tools_by_category(self, category: ToolCategory) -> List[OSINTTool]:
        return [tool for tool in self._tools.values() if tool.category == category]

    def search_tools(self, query: str) -> List[OSINTTool]:
        q = query.lower()
        results = []
        for tool in self._tools.values():
            if (q in tool.id.lower() or 
                q in tool.name.lower() or 
                q in tool.description.lower() or 
                q in tool.category.value.lower()):
                results.append(tool)
        return results
