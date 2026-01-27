"""
Polymarket Agent CLI - Typer-based CLI for Polymarket trading.
Install with: pip install -e .
Then run: poly --help
"""
import os
import sys
import subprocess
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

# Initialize
app = typer.Typer(
    name="poly",
    help="🎰 Polymarket Agent - AI-powered prediction market trading CLI",
    rich_markup_mode="markdown",
    no_args_is_help=True,
)
console = Console()

# ══════════════════════════════════════════════════════════════════════════════
# SETUP & CONFIG COMMANDS
# ══════════════════════════════════════════════════════════════════════════════

@app.command(rich_help_panel="Setup")
def setup():
    """
    🔧 **Interactive setup wizard** to configure API keys and preferences.
    
    Runs the full configuration flow including:
    - Private key setup
    - Risk profile selection
    - Market interests
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    setup_script = os.path.join(script_dir, "configure.py")
    subprocess.run([sys.executable, setup_script])


@app.command(rich_help_panel="Setup")
def config(
    key: Optional[str] = typer.Option(None, "--key", "-k", help="Config key to get/set"),
    value: Optional[str] = typer.Option(None, "--value", "-v", help="Value to set"),
):
    """
    ⚙️ **Get or set configuration** values directly.
    
    Examples:
    - `poly config --key RISK_PROFILE`
    - `poly config --key RISK_PROFILE --value DEGEN`
    """
    if key and value:
        # Set config
        cmd = ["clawdbot", "config", "set", f"skills.entries.polymarket-agent.env.{key}", value]
        try:
            subprocess.run(cmd, check=True)
            console.print(f"[green]✔ Set {key} = {value}[/green]")
        except Exception as e:
            console.print(f"[red]✘ Failed: {e}[/red]")
    elif key:
        # Get config
        cmd = ["clawdbot", "config", "get", f"skills.entries.polymarket-agent.env.{key}"]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            console.print(f"[cyan]{key}[/cyan] = {result.stdout.strip()}")
        except Exception as e:
            console.print(f"[red]✘ Failed: {e}[/red]")
    else:
        console.print("[yellow]Usage: poly config --key <KEY> [--value <VALUE>][/yellow]")


@app.command(rich_help_panel="Setup")
def doctor():
    """
    🩺 **Health check** - verify all dependencies and credentials are working.
    """
    console.print(Panel("🩺 Polymarket Agent Health Check", border_style="cyan"))
    
    checks = [
        ("Python", "python --version"),
        ("pip", "pip --version"),
        ("py-clob-client", "python -c \"import py_clob_client\""),
        ("requests", "python -c \"import requests\""),
        ("rich", "python -c \"import rich\""),
        ("typer", "python -c \"import typer\""),
    ]
    
    for name, cmd in checks:
        try:
            subprocess.run(cmd, shell=True, check=True, capture_output=True)
            console.print(f"  [green]✔[/green] {name}")
        except:
            console.print(f"  [red]✘[/red] {name} - NOT FOUND")
    
    # Check API Key
    key = os.getenv("POLYMARKET_KEY")
    if key:
        console.print(f"  [green]✔[/green] POLYMARKET_KEY configured")
    else:
        console.print(f"  [yellow]⚠[/yellow] POLYMARKET_KEY not set (run `poly setup`)")


# ══════════════════════════════════════════════════════════════════════════════
# MARKET COMMANDS
# ══════════════════════════════════════════════════════════════════════════════

@app.command(rich_help_panel="Markets")
def markets(
    query: str = typer.Argument("", help="Search query for markets"),
    limit: int = typer.Option(10, "--limit", "-l", help="Number of results"),
):
    """
    📊 **Search and list** active prediction markets.
    
    Examples:
    - `poly markets` (shows trending)
    - `poly markets "bitcoin"`
    - `poly markets "trump" --limit 5`
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, script_dir)
    
    try:
        from analyze import search_markets, print_market_table
        results = search_markets(query if query else None, limit)
        if results:
            print_market_table(results)
        else:
            console.print("[yellow]No markets found matching your query.[/yellow]")
    except ImportError as e:
        console.print(f"[red]Error loading tools: {e}. Run `poly doctor` to check.[/red]")


@app.command(rich_help_panel="Markets")
def watch(
    market_id: str = typer.Argument(..., help="Market ID or slug to watch"),
):
    """
    👁️ **Watch a specific market** - show real-time price updates.
    """
    console.print(f"[cyan]Watching market: {market_id}...[/cyan]")
    console.print("[yellow]Feature coming soon - WebSocket integration[/yellow]")


# ══════════════════════════════════════════════════════════════════════════════
# TRADING COMMANDS
# ══════════════════════════════════════════════════════════════════════════════

@app.command(rich_help_panel="Trading")
def buy(
    token_id: str = typer.Argument(..., help="Token ID to buy"),
    price: float = typer.Argument(..., help="Limit price (0.01 - 0.99)"),
    size: float = typer.Argument(..., help="Amount to buy"),
    confirm: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation"),
):
    """
    💰 **Place a BUY order** on a market outcome.
    
    Example: `poly buy <TOKEN_ID> 0.55 10 --yes`
    """
    if not confirm:
        typer.confirm(f"Buy {size} @ ${price} for token {token_id[:10]}...?", abort=True)
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    trade_script = os.path.join(script_dir, "trade.py")
    subprocess.run([sys.executable, trade_script, token_id, "BUY", str(price), str(size)])


@app.command(rich_help_panel="Trading")
def sell(
    token_id: str = typer.Argument(..., help="Token ID to sell"),
    price: float = typer.Argument(..., help="Limit price (0.01 - 0.99)"),
    size: float = typer.Argument(..., help="Amount to sell"),
    confirm: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation"),
):
    """
    💸 **Place a SELL order** on a market outcome.
    
    Example: `poly sell <TOKEN_ID> 0.75 5 --yes`
    """
    if not confirm:
        typer.confirm(f"Sell {size} @ ${price} for token {token_id[:10]}...?", abort=True)
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    trade_script = os.path.join(script_dir, "trade.py")
    subprocess.run([sys.executable, trade_script, token_id, "SELL", str(price), str(size)])


@app.command(rich_help_panel="Trading")
def positions():
    """
    📈 **View your current positions** and P&L.
    """
    key = os.getenv("POLYMARKET_KEY")
    if not key:
        console.print("[red]POLYMARKET_KEY not set. Run `poly setup` first.[/red]")
        raise typer.Exit(1)
    
    console.print("[cyan]Fetching positions...[/cyan]")
    # TODO: Implement via py-clob-client
    console.print("[yellow]Feature requires authenticated client. Coming soon.[/yellow]")


@app.command(rich_help_panel="Trading")
def orders():
    """
    📋 **View your open orders**.
    """
    key = os.getenv("POLYMARKET_KEY")
    if not key:
        console.print("[red]POLYMARKET_KEY not set. Run `poly setup` first.[/red]")
        raise typer.Exit(1)
    
    console.print("[cyan]Fetching open orders...[/cyan]")
    console.print("[yellow]Feature requires authenticated client. Coming soon.[/yellow]")


@app.command(rich_help_panel="Trading")
def balance():
    """
    💵 **Check your wallet balance** (USDC on Polygon).
    """
    key = os.getenv("POLYMARKET_KEY")
    if not key:
        console.print("[red]POLYMARKET_KEY not set. Run `poly setup` first.[/red]")
        raise typer.Exit(1)
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, script_dir)
    
    try:
        from trade import get_balance
        bal = get_balance()
        if bal is not None:
            console.print(Panel(
                f"[bold green]${bal:.2f} USDC[/bold green]",
                title="💵 Wallet Balance",
                border_style="green"
            ))
    except ImportError as e:
        console.print(f"[red]Error: {e}. Run `poly doctor` to check.[/red]")
    except Exception as e:
        console.print(f"[red]Failed to fetch balance: {e}[/red]")


# ══════════════════════════════════════════════════════════════════════════════
# AGENT COMMANDS
# ══════════════════════════════════════════════════════════════════════════════

@app.command(rich_help_panel="Agent")
def analyze(
    topic: str = typer.Argument(..., help="Topic or market slug to analyze"),
):
    """
    🧠 **AI-powered analysis** - Get trading recommendations.
    
    The agent will search news, compare to market odds, and suggest trades.
    """
    console.print(f"[cyan]Analyzing '{topic}'...[/cyan]")
    console.print("[yellow]This feature triggers Clawdbot agent analysis.[/yellow]")
    console.print("Ask Clawdbot: [green]'Analyze Polymarket opportunity for {topic}'[/green]")


@app.command(rich_help_panel="Agent")
def auto(
    enable: bool = typer.Argument(..., help="Enable or disable autonomous mode"),
):
    """
    🤖 **Toggle autonomous trading mode**.
    
    When enabled, the agent can execute trades without confirmation.
    ⚠️ USE WITH CAUTION.
    """
    status = "ENABLED" if enable else "DISABLED"
    console.print(f"[{'green' if enable else 'red'}]Autonomous mode: {status}[/]")
    # Store in config
    subprocess.run([
        "clawdbot", "config", "set",
        "skills.entries.polymarket-agent.env.AUTONOMOUS_MODE",
        str(enable).lower()
    ], capture_output=True)


# ══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

def main():
    app()

if __name__ == "__main__":
    main()
