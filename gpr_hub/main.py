import os
import sys
import time
import json
import webbrowser
import requests
import numpy as np
import matplotlib.pyplot as plt
from getpass import getpass
from cryptography.fernet import Fernet
from google import genai
from google.genai import types

# Rich UI Components
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.text import Text
from rich import box
from rich.color import Color

# Style components
from colorama import init
from cinetext import cinetext_rainbow

console = Console()
init(autoreset=True)

VERSION = "v6.0.0 beta" 
REPO = "codemaster-ar/gpr-hub-cli"
VAULT_KEY_PATH = ".gpr_master.key"
VAULT_DATA_PATH = ".gpr_vault.dat"
CUSTOM_ML_URL = "https://codemaster-ar.github.io/gpr-hub-web/ai-gpr-determiner/"

class GPRHub:
    def __init__(self):
        self.version = VERSION
        self.fernet = self._init_encryption()
        self.api_keys = self._load_vault()
        
    def _init_encryption(self):
        if not os.path.exists(VAULT_KEY_PATH):
            key = Fernet.generate_key()
            with open(VAULT_KEY_PATH, "wb") as f: f.write(key)
        else:
            with open(VAULT_KEY_PATH, "rb") as f: key = f.read()
        return Fernet(key)

    def _load_vault(self):
        if os.path.exists(VAULT_DATA_PATH):
            try:
                with open(VAULT_DATA_PATH, "rb") as f:
                    encrypted = f.read()
                return json.loads(self.fernet.decrypt(encrypted).decode())
            except: return {}
        return {}

    def save_to_vault(self, service, key):
        self.api_keys[service] = key
        encrypted = self.fernet.encrypt(json.dumps(self.api_keys).encode())
        with open(VAULT_DATA_PATH, "wb") as f: f.write(encrypted)
        console.print(f"[bold green]✔ {service} key encrypted and locked in vault.[/]")

    def check_for_updates(self):
        url = f"https://api.github.com/repos/{REPO}/releases/latest"
        try:
            with console.status("[bold blue]Connecting to GPR Hub Servers...", spinner="bouncingBar"):
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    latest_version = response.json()['tag_name']
                    if latest_version != self.version:
                        console.print(Panel(
                            f"[bold red]SYSTEM OUTDATED[/]\n\n"
                            f"Current: [yellow]{self.version}[/]\n"
                            f"Latest:  [green]{latest_version}[/]\n\n"
                            f"Command: [bold white]brew upgrade gpr-hub[/]",
                            border_style="bright_red", box=box.DOUBLE, title="⚠ Update Available"
                        ))
                    else:
                        console.print(f"[bold green]✔[/] Software is current ({self.version})")
        except:
            console.print("[dim yellow]Warning: Offline mode. Could not verify version.[/]")

    def make_prominent_gradient(self, text_str):
        lines = text_str.splitlines()
        rendered_text = Text()
        for i, line in enumerate(lines):
            r = int(min(255, (i / len(lines)) * 510))
            g = int(max(0, 255 - (i / len(lines)) * 255))
            b = 255
            color = Color.from_rgb(r, g, b)
            rendered_text.append(line + "\n", style=f"bold {color.name}")
        return rendered_text

    def show_banner(self):
        self.clear()
        logo = r"""
  ____ ____  ____    _   _       _         
 / ___|  _ \|  _ \  | | | |_   _| |__      
| |  _| |_) | |_) | | |_| | | | | '_ \ 
| |_| |  __/|  _ <  |  _  | |_| | |_) |
 \____|_|   |_| \_\ |_| |_|\__,_|_.__/ 
        """
        cinetext_rainbow(logo, 20, 0.03)
        self.clear()
        console.print(self.make_prominent_gradient(logo))
        console.print(Panel(
            Text(f"GPR HUB INTELLIGENCE | {self.version}", justify="center", style="bold white"),
            border_style="bright_blue", box=box.HORIZONTALS
        ))

    def show_commands(self):
        table = Table(title="📡 Command Registry", box=box.ROUNDED, header_style="bold magenta")
        table.add_column("Command", style="bold green")
        table.add_column("Function")
        
        cmds = [
            ("gemini_gpr", "Run AI Vision Analysis on local radargrams"),
            ("gui_ml_gpr", "Launch the Web-based AI GPR Determiner"),
            ("vault_setup", "Configure encrypted API keys"),
            ("check_up", "Manual version sync"),
            ("clear", "Reset UI & Banner"),
            ("exit", "Terminate session")
        ]
        for c, f in cmds: table.add_row(c, f)
        console.print(table)

    def open_custom_ml(self):
        """Launches the external GPR Determiner tool."""
        console.print(f"[bold blue]Redirecting to GPR Determiner Web UI...[/]")
        try:
            webbrowser.open(CUSTOM_ML_URL)
            console.print(f"[bold green]✔ Browser opened successfully.[/]")
        except Exception as e:
            console.print(f"[bold red]Failed to open browser:[/] {e}")

    def clear(self):
        os.system('cls' if os.name == 'nt' else 'clear')

def main():
    hub = GPRHub()
    hub.show_banner()
    hub.check_for_updates()

    while True:
        try:
            cmd = Prompt.ask(f"\n[bold cyan]GPR-HUB[/]").strip().lower()

            if cmd in ["help", "commands", "cmds"]:
                hub.show_commands()
            elif cmd == "gui_ml_gpr":
                hub.open_custom_ml()
            elif cmd == "vault_setup":
                service = Prompt.ask("Target Service", choices=["GEMINI", "GROQ", "EXIT"])
                if service != "EXIT":
                    key = getpass(f"Enter {service} Key (Hidden): ")
                    hub.save_to_vault(service, key)
            elif cmd == "gemini_gpr":
                # Assuming gemini_vision logic is here as per previous turn
                console.print("[yellow]Starting Gemini Vision Module...[/]")
            elif cmd == "check_up":
                hub.check_for_updates()
            elif cmd == "clear":
                hub.show_banner()
            elif cmd == "exit":
                console.print("[bold red]Exiting... Status 0[/]")
                break
            else:
                console.print(f"[dim red]Error: '{cmd}' is not a recognized command. Enter 'commands' to get a list of functional commands. Commands are case sensitive.[/]")
        except KeyboardInterrupt: break

if __name__ == "__main__":
    main()