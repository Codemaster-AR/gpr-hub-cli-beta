import os
import sys
import time
import json
import datetime
import webbrowser
import requests
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
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
from rich.live import Live
from rich.text import Text
from rich import box
from rich.color import Color
from KeyboardGate import KeyboardGate
# Style components
from colorama import init, Fore, Style
from cinetext import cinetext_type, cinetext_rainbow, cinetext_pulse

# Initialization
console = Console()
init(autoreset=True)

# --- GLOBAL CONFIGURATION ---
VERSION = "v6.0.0-beta" # Set to trigger update alert
REPO = "codemaster-ar/gpr-hub-cli-beta"
VAULT_KEY_PATH = ".gpr_master.key"
VAULT_DATA_PATH = ".gpr_vault.dat"
HISTORY_PATH = ".gpr_history.json"
CUSTOM_ML_URL = "https://codemaster-ar.github.io/gpr-hub-web/ai-gpr-determiner/"

# Physical Constants for GPR
SOIL_DIELECTRICS = {
    "air": 1.0,
    "ice": 3.2,
    "dry_sand": 4.0,
    "granite": 5.0,
    "concrete": 6.5,
    "limestone": 7.0,
    "wet_sand": 25.0,
    "clay": 15.0,
    "fresh_water": 81.0
}

class GPRHub:
    def __init__(self):
        self.version = VERSION
        self.session_id = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        self.session_start = datetime.datetime.now()
        
        # Security Initialization
        self.fernet = self._init_encryption_engine()
        self.api_keys = self._load_secure_vault()
        
        # State tracking
        self.last_command = "None"

    # -------------------------------------------------------------------------
    # SECURITY & ENCRYPTION ENGINE
    # -------------------------------------------------------------------------
    def _init_encryption_engine(self):
        """Generates or loads the master AES key for Fernet encryption."""
        if not os.path.exists(VAULT_KEY_PATH):
            key = Fernet.generate_key()
            with open(VAULT_KEY_PATH, "wb") as f:
                f.write(key)
            return Fernet(key)
        else:
            with open(VAULT_KEY_PATH, "rb") as f:
                return Fernet(f.read())

    def _load_secure_vault(self):
        """Decrypts the local data file to retrieve API keys."""
        if os.path.exists(VAULT_DATA_PATH):
            try:
                with open(VAULT_DATA_PATH, "rb") as f:
                    encrypted_blob = f.read()
                decrypted_json = self.fernet.decrypt(encrypted_blob).decode()
                return json.loads(decrypted_json)
            except Exception as e:
                console.print(f"[bold red]Vault Decryption Error:[/] {e}")
                return {}
        return {}

    def run_vault_setup(self):
        """Interactive command to encrypt and store API keys."""
        console.print(Panel("[bold yellow]GPR SECURE VAULT SETUP[/]\nEncrypting keys with AES-128 Symmetric Encryption.", border_style="yellow"))
        
        service = Prompt.ask("Select Service", choices=["GEMINI", "GROQ", "ALL", "EXIT"])
        if service == "EXIT": return

        if service in ["GEMINI", "ALL"]:
            key = getpass("Enter Google Gemini API Key: ")
            self.api_keys["GEMINI"] = key
        
        if service in ["GROQ", "ALL"]:
            key = getpass("Enter Groq API Key: ")
            self.api_keys["GROQ"] = key

        # Encrypt and write to disk
        try:
            encrypted_data = self.fernet.encrypt(json.dumps(self.api_keys).encode())
            with open(VAULT_DATA_PATH, "wb") as f:
                f.write(encrypted_data)
            console.print("[bold green]✔ Success:[/] Keys encrypted and stored in .gpr_vault.dat")
        except Exception as e:
            console.print(f"[bold red]Encryption Failed:[/] {e}")

    # -------------------------------------------------------------------------
    # CORE VISUALIZATION & ANALYSIS
    # -------------------------------------------------------------------------
    def run_open_gpr(self):
        """The classic GPR Visualizer using Numpy and Matplotlib."""
        console.print(Panel("[bold cyan]GPR RADARGRAM VISUALIZER[/]", subtitle="Numpy + Matplotlib Engine"))
        
        path = Prompt.ask("Enter the full path to the image file").strip().replace('"', '').replace("'", "")
        
        if not os.path.exists(path):
            console.print(f"[bold red]Error:[/] File not found at {path}")
            return

        with console.status("[bold green]Processing radargram signal data...", spinner="earth"):
            try:
                # Load image and convert to grayscale for signal analysis
                raw_img = Image.open(path).convert('L')
                gpr_matrix = np.array(raw_img)
                
                # Plotting Configuration
                plt.figure(figsize=(12, 7))
                plt.imshow(gpr_matrix, cmap='bone', aspect='auto')
                plt.title(f"Subsurface Profile: {os.path.basename(path)}", fontsize=14)
                plt.xlabel("Horizontal Scan Distance (Samples)", fontweight='bold')
                plt.ylabel("Vertical Travel Time / Depth (Pixels)", fontweight='bold')
                plt.colorbar(label='Signal Intensity / Amplitude')
                
                console.print(f"[bold green]✔ Signal Processing Complete.[/] Resolution: {raw_img.size[0]}x{raw_img.size[1]}")
                console.print("[yellow]Launching external plotting window...[/]")
                plt.show()
                
            except Exception as e:
                console.print(f"[bold red]Critical Plotting Error:[/] {e}")

    def run_subsurface_calc(self):
        """Advanced Physics Calculator for GPR Depth/Velocity."""
        console.print(Panel("[bold yellow]SUBSURFACE VELOCITY & DEPTH CALCULATOR[/]"))
        
        # Display library
        lib_table = Table(title="Common Dielectric Constants (εr)", box=box.SIMPLE)
        lib_table.add_column("Material", style="cyan")
        lib_table.add_column("εr Value", style="magenta")
        for mat, val in SOIL_DIELECTRICS.items():
            lib_table.add_row(mat.replace("_", " ").title(), str(val))
        console.print(lib_table)

        try:
            er = float(Prompt.ask("Enter Dielectric Constant (εr)"))
            t_ns = float(Prompt.ask("Enter Two-Way Travel Time (nanoseconds)"))
            
            # Physics: v = c / sqrt(er) where c is ~0.3 m/ns
            velocity = 0.3 / np.sqrt(er)
            depth = (velocity * t_ns) / 2
            
            console.print("\n" + "-"*30)
            console.print(f"Calculated Velocity: [bold green]{velocity:.4f} m/ns[/]")
            console.print(f"Estimated Target Depth: [bold green]{depth:.2f} meters[/]")
            console.print("-"*30)
        except Exception as e:
            console.print(f"[red]Input Error:[/] {e}")

    # -------------------------------------------------------------------------
    # UTILITIES & UI
    # -------------------------------------------------------------------------
    def clear(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def check_for_updates(self):
        """GitHub API version check."""
        url = f"https://api.github.com/repos/{REPO}/releases/latest"
        try:
            response = requests.get(url, timeout=3)
            if response.status_code == 200:
                latest = response.json()['tag_name']
                if latest != self.version:
                    console.print(Panel(
                        f"[bold red]⚠ UPDATE AVAILABLE[/]\nLocal: {self.version} | Latest: {latest}\n"
                        f"Run: [bold]brew upgrade gpr-hub-cli[/]",
                        border_style="bright_yellow", box=box.DOUBLE
                    ))
                else:
                    console.print(f"[dim green]✔ System is up to date ({self.version})[/]")
        except:
            console.print("[dim yellow]! Could not contact update server.[/]")

    def make_gradient_banner(self, text_str):
        """Logic to create a vertical color gradient for the logo."""
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
        console.print(self.make_gradient_banner(logo))
        console.print(Panel(
            Text(f"GPR HUB INTELLIGENCE SUITE | {self.version}", justify="center", style="bold white"),
            subtitle=f"Session: {self.session_id}",
            border_style="bright_blue", box=box.HORIZONTALS
        ))

    def show_commands(self):
        table = Table(title="📡 COMMAND REGISTRY", box=box.ROUNDED, header_style="bold magenta")
        table.add_column("Command", style="bold green", no_wrap=True)
        table.add_column("Category", style="dim")
        table.add_column("Description")
        
        cmds = [
            ("open_gpr", "Analysis", "Open radargram in interactive plotter (Numpy/Matplotlib)"),
            ("gemini_gpr", "AI", "Advanced Vision analysis of subsurface anomalies"),
            ("gui_ml_gpr", "Web", "Open the GitHub ML GPR Determiner Tool"),
            ("subsurface", "Physics", "Calculate depth/velocity using dielectric constants"),
            ("vault_setup", "Security", "Configure and encrypt API keys for Gemini/Groq"),
            ("history", "Session", "View current session activity logs"),
            ("clear", "UI", "Reset the terminal and redraw banner"),
            ("exit", "System", "Safely terminate the application")
        ]
        for c, cat, desc in cmds:
            table.add_row(c, cat, desc)
        console.print(table)

    def run_sys_diag(self):
        diag_table = Table(title="System Diagnostics")
        diag_table.add_column("Component")
        diag_table.add_column("Status")
        diag_table.add_row("Encryption Engine", "Operational" if self.fernet else "FAILED")
        diag_table.add_row("Vault Status", "LOADED" if self.api_keys else "EMPTY")
        diag_table.add_row("Uptime", str(datetime.datetime.now() - self.session_start))
        console.print(diag_table)

# -------------------------------------------------------------------------
# MAIN EXECUTION LOOP
# -------------------------------------------------------------------------
def main():
    gate = KeyboardGate()
    gate.KeyboardGateDisable()
    hub = GPRHub()
    hub.show_banner()
    hub.check_for_updates()
    gate.KeyboardGateEnable()

    while True:
        try:
            cmd = Prompt.ask(f"\n[bold cyan]GPR-HUB[/]").strip().lower()
            hub.last_command = cmd

            if cmd in ["help", "commands", "cmds"]:
                hub.show_commands()
            elif cmd == "open_gpr":
                hub.run_open_gpr()
            elif cmd == "gui_ml_gpr":
                console.print("[blue]Redirecting to Custom Web ML Tool...[/]")
                webbrowser.open(CUSTOM_ML_URL)
            elif cmd == "subsurface":
                hub.run_subsurface_calc()
            elif cmd == "vault_setup":
                hub.run_vault_setup()
            elif cmd == "history":
                hub.run_sys_diag()
            elif cmd == "gemini_gpr":
                console.print("[bold yellow]AI Intelligence Module Starting...[/]")
                # Placeholder for the vision logic (Requires keys from vault)
            elif cmd == "clear":
                hub.show_banner()
            elif cmd == "exit":
                console.print("[bold red]Shutting down GPR Intelligence Suite. Goodbye.[/]")
                sys.exit(0)
            else:
                console.print(f"[dim red]Error: '{cmd}' not recognized. Type 'commands' for a list.")
        
        except KeyboardInterrupt:
            console.print("\n[yellow]Interrupted by user. Exiting...[/]")
            break

if __name__ == "__main__":
    main()