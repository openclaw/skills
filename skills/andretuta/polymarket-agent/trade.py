import os
import sys
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs
from py_clob_client.order_builder.constants import BUY, SELL
from rich.console import Console

console = Console()

def get_client():
    key = os.getenv("POLYMARKET_KEY")
    if not key:
        console.print("[red]Error: POLYMARKET_KEY not found in environment.[/red]")
        console.print("Please run [yellow]python skills/polymarket-agent/setup.py[/yellow] to configure.")
        sys.exit(1)
        
    host = "https://clob.polymarket.com"
    chain_id = 137 # Polygon
    
    try:
        # Initial client to derive creds
        temp_client = ClobClient(host, key=key, chain_id=chain_id)
        creds = temp_client.create_or_derive_api_creds()
        
        # Authenticated client
        client = ClobClient(host, key=key, chain_id=chain_id, creds=creds)
        return client
    except Exception as e:
        console.print(f"[red]Authentication Failed: {e}[/red]")
        return None

def get_balance():
    """Get USDC balance from Polymarket account"""
    client = get_client()
    if not client:
        return None
    
    try:
        # Get collateral balance (USDC)
        balance_info = client.get_balance_allowance(asset_type="COLLATERAL")
        balance = float(balance_info.get("balance", 0)) / 1e6  # USDC has 6 decimals
        return balance
    except Exception as e:
        console.print(f"[red]Error fetching balance: {e}[/red]")
        return None

def place_order(token_id, side, price, size):
    client = get_client()
    if not client:
        return
        
    order_side = BUY if side.upper() == "BUY" else SELL
    
    try:
        resp = client.create_and_post_order(OrderArgs(
            token_id=token_id,
            price=float(price),
            size=float(size),
            side=order_side
        ))
        return resp
    except Exception as e:
        console.print(f"[red]Trade Failed: {e}[/red]")
        return None

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Usage: python trade.py <token_id> <BUY/SELL> <price> <size>")
        sys.exit(1)
        
    tid = sys.argv[1]
    side = sys.argv[2]
    price = sys.argv[3]
    size = sys.argv[4]
    
    res = place_order(tid, side, price, size)
    if res:
        console.print(f"[green]Order Placed! ID: {res.get('orderID')}[/green]")
