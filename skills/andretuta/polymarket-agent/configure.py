#!/usr/bin/env python
"""
Polymarket Agent Configuration Wizard
Run with: python configure.py
"""

def main():
    # Imports inside main to avoid issues during package discovery
    import sys
    import subprocess
    import time
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn
    import questionary
    
    console = Console()
    
    BANNER = r"""
[bold cyan]
   ___      _                            _        _   
  / _ \___ | |_   _ _ __ ___   __ _ _ __| | _____| |_ 
 / /_)/ _ \| | | | | '_ ` _ \ / _` | '__| |/ / _ \ __|
/ ___/ (_) | | |_| | | | | | | (_| | |  |   <  __/ |_ 
\/    \___/|_|\__, |_| |_| |_|\__,_|_|  |_|\_\___|\__|
              |___/                                   
        [yellow]Polymarket Agent Setup[/yellow]
[/bold cyan]
"""
    
    def install_dependencies():
        """Installs required packages from requirements.txt"""
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                transient=True,
            ) as progress:
                progress.add_task(description="Installing dependencies...", total=None)
                subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "--quiet"])
            console.print("[green]✔ Dependencies installed successfully.[/green]")
        except subprocess.CalledProcessError:
            console.print("[red]✘ Failed to install dependencies. Please run 'pip install -r requirements.txt' manually.[/red]")
            sys.exit(1)
    
    def configure_clawdbot(key_name, value):
        """Sets a configuration value in Clawdbot global config"""
        cmd = ["clawdbot", "config", "set", f"skills.entries.polymarket-agent.env.{key_name}", value]
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return True
        except FileNotFoundError:
            console.print("[yellow]⚠ 'clawdbot' CLI not found. Skipping persistent config (env only).[/yellow]")
            return False
        except subprocess.CalledProcessError:
            console.print(f"[red]✘ Failed to set {key_name} in Clawdbot config.[/red]")
            return False
    
    console.print(BANNER)
    console.print(Panel(
        "Welcome to the Polymarket Agent Setup.\n"
        "This will configure your wallet for trading.",
        title="Setup",
        border_style="cyan"
    ))

    # 1. Install Dependencies
    if questionary.confirm("Install Python dependencies now?", default=True).ask():
        install_dependencies()

    # 2. API Key (Polymarket / Private Key)
    console.print("\n[bold]🔐 Wallet Configuration[/bold]")
    console.print("To trade on Polymarket, you need a [green]Polygon Wallet Private Key[/green].")
    console.print("This key is stored [cyan]securely in Clawdbot's internal configuration[/cyan].")
    console.print("[dim]Your key never leaves your machine.[/dim]\n")
    
    private_key = questionary.password("Enter your Private Key (starts with 0x...):").ask()

    if private_key:
        if not private_key.startswith("0x"):
            console.print("[yellow]⚠ Key should start with 0x. Prepending...[/yellow]")
            private_key = "0x" + private_key
            
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            progress.add_task(description="Storing credentials securely...", total=None)
            time.sleep(1)
            
            success = configure_clawdbot("POLYMARKET_KEY", private_key)
            
            if success:
                console.print("[green]✔ Wallet configured successfully![/green]")
            else:
                console.print("[yellow]⚠ Could not save to Clawdbot config.[/yellow]")
                console.print("[dim]Set POLYMARKET_KEY environment variable manually.[/dim]")
    else:
        console.print("[yellow]⚠ No key provided. You can set it later with:[/yellow]")
        console.print("[cyan]poly config --key POLYMARKET_KEY --value <your_key>[/cyan]")

    # Done!
    console.print("\n" + "─" * 50)
    console.print("[bold green]✅ Setup Complete![/bold green]\n")
    console.print("You can now ask Clawdbot things like:")
    console.print("  [cyan]• 'Analyze Polymarket opportunities'[/cyan]")
    console.print("  [cyan]• 'What should I bet on?'[/cyan]")
    console.print("  [cyan]• 'Search crypto markets on Polymarket'[/cyan]")
    console.print("\nOr use the CLI directly:")
    console.print("  [dim]poly markets --limit 10[/dim]")
    console.print("  [dim]poly doctor[/dim]")

if __name__ == "__main__":
    import sys
    try:
        main()
    except KeyboardInterrupt:
        print("\n[yellow]Setup cancelled.[/yellow]")
        sys.exit(0)
