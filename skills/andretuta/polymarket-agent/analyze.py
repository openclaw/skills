"""
Polymarket Market Analysis Tool
Fetches market data from Polymarket's Gamma API.
"""
import os
import requests
import json
from rich.console import Console
from rich.table import Table

GAMMA_API = "https://gamma-api.polymarket.com"

console = Console()

def get_interests():
    """Get user interests from environment or default"""
    interests = os.getenv("INTERESTS", "Crypto,Politics")
    return [i.strip() for i in interests.split(",")]

def search_markets(query=None, limit=10):
    """
    Search for active markets.
    If query is None or empty, returns popular markets without text filtering.
    """
    params = {
        "limit": limit,
        "active": "true",
        "closed": "false",
        "order": "volume24hr",
        "ascending": "false"  # Descending order by volume
    }
    
    url = f"{GAMMA_API}/markets"
    
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            console.print(f"[red]API Error: {response.status_code}[/red]")
            return []
            
        markets = response.json()
        
        # If no query, return all fetched markets (no client-side filter)
        if not query or query.strip() == "":
            results = []
            for m in markets[:limit]:
                results.append(_format_market(m))
            return results
        
        # Otherwise, filter by query
        query_lower = query.lower()
        results = []
        for m in markets:
            question = m.get("question", "").lower()
            slug = m.get("slug", "").lower()
            description = m.get("description", "").lower()
            
            if query_lower in question or query_lower in slug or query_lower in description:
                results.append(_format_market(m))
                if len(results) >= limit:
                    break
                
        return results
        
    except requests.RequestException as e:
        console.print(f"[red]Network Error: {e}[/red]")
        return []

def _format_market(m):
    """Format a market dict for display"""
    outcomes = []
    outcome_prices = []
    
    try:
        outcomes = json.loads(m.get("outcomes", "[]"))
        outcome_prices = json.loads(m.get("outcomePrices", "[]"))
    except (json.JSONDecodeError, TypeError):
        pass
    
    prices_fmt = []
    if outcomes and outcome_prices:
        for o, p in zip(outcomes, outcome_prices):
            try:
                prices_fmt.append(f"{o}: ${float(p):.2f}")
            except (ValueError, TypeError):
                prices_fmt.append(f"{o}: ?")
    
    volume = m.get("volume24hr", 0)
    try:
        volume = float(volume) if volume else 0
    except (ValueError, TypeError):
        volume = 0
    
    return {
        "id": m.get("id"),
        "question": m.get("question", "Unknown"),
        "prices": ", ".join(prices_fmt) if prices_fmt else "N/A",
        "volume": volume,
        "clobTokenIds": m.get("clobTokenIds"),
        "slug": m.get("slug")
    }

def print_market_table(markets):
    """Print markets in a nice table"""
    table = Table(title="📊 Polymarket Opportunities")
    table.add_column("Question", style="cyan", max_width=50)
    table.add_column("Prices", style="green")
    table.add_column("Volume (24h)", style="magenta", justify="right")
    
    for m in markets:
        vol = m.get('volume', 0)
        vol_str = f"${vol:,.0f}" if vol >= 1 else "$0"
        table.add_row(
            m['question'][:50] + "..." if len(m['question']) > 50 else m['question'],
            m['prices'],
            vol_str
        )
        
    console.print(table)

if __name__ == "__main__":
    # Test execution
    console.print("[cyan]Searching for popular markets...[/cyan]")
    res = search_markets(None, 5)
    if res:
        print_market_table(res)
    else:
        console.print("[yellow]No markets found.[/yellow]")
