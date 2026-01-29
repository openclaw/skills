#!/usr/bin/env python3
import argparse
import os
import sys
import json
import quiverquant
from datetime import datetime, timedelta

def get_quiver_token():
    # Try environment variable first
    token = os.environ.get("QUIVER_API_KEY")
    if token:
        return token
    
    # Try TOOLS.md or a local config file (simplified for this example)
    # In a real setup, we might parse TOOLS.md
    
    # Fallback to interactive prompt if allowed (unlikely in this context) or error
    print("Error: QUIVER_API_KEY environment variable not set.", file=sys.stderr)
    sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Query Quiver Quantitative API")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Congress Trading
    congress_parser = subparsers.add_parser("congress", help="Get congress trading data")
    congress_parser.add_argument("--ticker", help="Filter by ticker (e.g. AAPL)")
    congress_parser.add_argument("--politician", help="Filter by politician name")
    congress_parser.add_argument("--house", choices=["senate", "house"], help="Filter by house (senate/house)")
    
    # Lobbying
    lobbying_parser = subparsers.add_parser("lobbying", help="Get corporate lobbying data")
    lobbying_parser.add_argument("ticker", nargs="?", help="Ticker symbol")

    # Gov Contracts
    contracts_parser = subparsers.add_parser("contracts", help="Get government contracts")
    contracts_parser.add_argument("ticker", nargs="?", help="Ticker symbol")

    # Insiders
    insider_parser = subparsers.add_parser("insiders", help="Get insider transactions")
    insider_parser.add_argument("ticker", nargs="?", help="Ticker symbol")

    args = parser.parse_args()

    token = get_quiver_token()
    quiver = quiverquant.quiver(token)

    try:
        df = None
        if args.command == "congress":
            if args.politician:
                df = quiver.congress_trading(args.politician, politician=True)
            elif args.ticker:
                df = quiver.congress_trading(args.ticker)
            else:
                df = quiver.congress_trading()
                
            # Filter by house if specified (post-processing since API might not support it directly in one call)
            if args.house and df is not None:
                if "House" in df.columns: # Adjust column name based on actual API response
                     df = df[df["House"] == args.house] # Pseudo-code, need to verify exact column name
        
        elif args.command == "lobbying":
            if args.ticker:
                df = quiver.lobbying(args.ticker)
            else:
                df = quiver.lobbying()

        elif args.command == "contracts":
            if args.ticker:
                df = quiver.gov_contracts(args.ticker)
            else:
                df = quiver.gov_contracts()
                
        elif args.command == "insiders":
            if args.ticker:
                df = quiver.insiders(args.ticker)
            else:
                df = quiver.insiders()

        if df is not None and not df.empty:
            # Output as JSON for easy parsing by the agent
            print(df.to_json(orient="records", date_format="iso"))
        else:
            print("[]") # Empty JSON array

    except Exception as e:
        print(f"Error querying Quiver API: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
