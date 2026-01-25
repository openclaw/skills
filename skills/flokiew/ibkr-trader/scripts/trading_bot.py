#!/usr/bin/env python3
"""
IBKR Trading Bot Template
A starting point for building automated trading strategies.

Customize the strategy() function to implement your trading logic.
"""

import requests
import urllib3
import json
import os
from datetime import datetime
from dataclasses import dataclass
from typing import Optional, List, Dict

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuration
BASE_URL = os.getenv("IBEAM_GATEWAY_BASE_URL", "https://localhost:5000")
ACCOUNT_ID = os.getenv("IBKR_ACCOUNT_ID", "")  # Set your account ID

@dataclass
class Position:
    symbol: str
    conid: int
    quantity: float
    avg_cost: float
    market_value: float
    unrealized_pnl: float

@dataclass
class Quote:
    conid: int
    symbol: str
    last_price: float
    bid: float
    ask: float
    volume: int

class IBKRClient:
    """Simple IBKR Client Portal API wrapper."""
    
    def __init__(self, base_url: str = BASE_URL, account_id: str = ACCOUNT_ID):
        self.base_url = base_url
        self.account_id = account_id
        self.session = requests.Session()
        self.session.verify = False
    
    def _get(self, endpoint: str, params: dict = None) -> dict:
        r = self.session.get(f"{self.base_url}{endpoint}", params=params, timeout=15)
        return r.json() if r.text else {}
    
    def _post(self, endpoint: str, data: dict = None) -> dict:
        r = self.session.post(f"{self.base_url}{endpoint}", json=data, timeout=15)
        return r.json() if r.text else {}
    
    def is_authenticated(self) -> bool:
        """Check if session is authenticated."""
        try:
            status = self._get("/v1/api/iserver/auth/status")
            return status.get("authenticated", False)
        except:
            return False
    
    def get_accounts(self) -> List[dict]:
        """Get list of accounts."""
        return self._get("/v1/api/portfolio/accounts")
    
    def get_balance(self) -> dict:
        """Get account balance/summary."""
        return self._get(f"/v1/api/portfolio/{self.account_id}/summary")
    
    def get_positions(self) -> List[Position]:
        """Get current positions."""
        data = self._get(f"/v1/api/portfolio/{self.account_id}/positions/0")
        positions = []
        for p in data if isinstance(data, list) else []:
            positions.append(Position(
                symbol=p.get("contractDesc", ""),
                conid=p.get("conid", 0),
                quantity=p.get("position", 0),
                avg_cost=p.get("avgCost", 0),
                market_value=p.get("mktValue", 0),
                unrealized_pnl=p.get("unrealizedPnl", 0)
            ))
        return positions
    
    def search_symbol(self, symbol: str) -> Optional[int]:
        """Search for a symbol and return its conid."""
        data = self._get("/v1/api/iserver/secdef/search", {"symbol": symbol})
        if data and len(data) > 0:
            return data[0].get("conid")
        return None
    
    def get_quote(self, conid: int) -> Optional[Quote]:
        """Get market data snapshot for a conid."""
        # Request snapshot
        self._get("/v1/api/iserver/marketdata/snapshot", {
            "conids": str(conid),
            "fields": "31,84,86,87,88"  # last, bid, ask, volume, close
        })
        # Get data (may need retry)
        for _ in range(3):
            data = self._get("/v1/api/iserver/marketdata/snapshot", {
                "conids": str(conid),
                "fields": "31,84,86,87,88"
            })
            if data and len(data) > 0:
                d = data[0]
                if d.get("31"):  # has last price
                    return Quote(
                        conid=conid,
                        symbol=d.get("symbol", ""),
                        last_price=float(d.get("31", 0)),
                        bid=float(d.get("84", 0)),
                        ask=float(d.get("86", 0)),
                        volume=int(d.get("87", 0))
                    )
        return None
    
    def place_order(self, conid: int, side: str, quantity: int, 
                    order_type: str = "MKT", limit_price: float = None) -> dict:
        """
        Place an order.
        
        Args:
            conid: Contract ID
            side: "BUY" or "SELL"
            quantity: Number of shares
            order_type: "MKT", "LMT", "STP", etc.
            limit_price: Price for limit orders
        """
        order = {
            "conid": conid,
            "orderType": order_type,
            "side": side,
            "quantity": quantity,
            "tif": "DAY"
        }
        if limit_price and order_type == "LMT":
            order["price"] = limit_price
        
        # Place order
        result = self._post(f"/v1/api/iserver/account/{self.account_id}/orders", {
            "orders": [order]
        })
        
        # Handle confirmation if needed
        if isinstance(result, list) and len(result) > 0:
            if result[0].get("messageIds"):
                # Confirm the order
                confirm = self._post(f"/v1/api/iserver/reply/{result[0]['id']}", {
                    "confirmed": True
                })
                return confirm
        
        return result
    
    def get_orders(self) -> List[dict]:
        """Get open orders."""
        return self._get("/v1/api/iserver/account/orders")
    
    def cancel_order(self, order_id: str) -> dict:
        """Cancel an order."""
        return self._post(f"/v1/api/iserver/account/{self.account_id}/order/{order_id}", {
            "delete": True
        })


def strategy(client: IBKRClient):
    """
    YOUR TRADING STRATEGY HERE
    
    This function is called by the main loop.
    Implement your buy/sell logic here.
    """
    # Example: Simple momentum strategy
    watchlist = ["AAPL", "GOOGL", "MSFT"]
    
    for symbol in watchlist:
        conid = client.search_symbol(symbol)
        if not conid:
            continue
        
        quote = client.get_quote(conid)
        if not quote:
            continue
        
        print(f"{symbol}: ${quote.last_price:.2f}")
        
        # Add your trading logic here
        # Example:
        # if should_buy(quote):
        #     client.place_order(conid, "BUY", 1)


def main():
    print("🏦 IBKR Trading Bot")
    print("=" * 40)
    
    client = IBKRClient()
    
    if not client.is_authenticated():
        print("❌ Not authenticated. Run authenticate.sh first.")
        return
    
    print("✅ Authenticated")
    
    # Get account info
    accounts = client.get_accounts()
    if accounts:
        client.account_id = accounts[0]["accountId"]
        print(f"📊 Account: {client.account_id}")
    
    # Get balance
    balance = client.get_balance()
    cash = balance.get("totalcashvalue", {}).get("amount", 0)
    print(f"💰 Cash: ${cash:,.2f}")
    
    # Get positions
    positions = client.get_positions()
    print(f"📈 Positions: {len(positions)}")
    for p in positions:
        print(f"   {p.symbol}: {p.quantity} @ ${p.avg_cost:.2f} (P&L: ${p.unrealized_pnl:.2f})")
    
    print()
    print("Running strategy...")
    strategy(client)


if __name__ == "__main__":
    main()
