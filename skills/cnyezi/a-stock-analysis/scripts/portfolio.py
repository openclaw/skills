#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
A股持仓管理工具

Usage:
    uv run portfolio.py show                           # 显示持仓
    uv run portfolio.py add 600789 --cost 10.5 --qty 1000   # 添加持仓
    uv run portfolio.py update 600789 --cost 10.2          # 更新成本
    uv run portfolio.py remove 600789                      # 删除持仓
    uv run portfolio.py analyze                            # 持仓分析(含分时)
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# 导入同目录的 analyze 模块
sys.path.insert(0, os.path.dirname(__file__))
from analyze import analyze_stock, format_realtime, format_minute_analysis


PORTFOLIO_FILE = Path.home() / ".clawdbot" / "skills" / "a-stock-analysis" / "portfolio.json"


def load_portfolio() -> dict:
    """加载持仓数据"""
    if PORTFOLIO_FILE.exists():
        with open(PORTFOLIO_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"positions": [], "updated_at": None}


def save_portfolio(data: dict):
    """保存持仓数据"""
    PORTFOLIO_FILE.parent.mkdir(parents=True, exist_ok=True)
    data["updated_at"] = datetime.now().isoformat()
    with open(PORTFOLIO_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def show_portfolio():
    """显示持仓"""
    portfolio = load_portfolio()
    positions = portfolio.get("positions", [])
    
    if not positions:
        print("暂无持仓记录")
        return
    
    print("=" * 70)
    print("当前持仓")
    print("=" * 70)
    print(f"{'股票':<10} {'代码':<8} {'成本':<8} {'数量':<8} {'市值估算':<12}")
    print("-" * 70)
    
    total_cost = 0
    for pos in positions:
        cost_value = pos["cost"] * pos["quantity"]
        total_cost += cost_value
        print(f"{pos.get('name', 'N/A'):<10} {pos['code']:<8} {pos['cost']:<8.3f} {pos['quantity']:<8} {cost_value:<12.0f}")
    
    print("-" * 70)
    print(f"总成本: {total_cost:.0f} 元")
    print(f"更新时间: {portfolio.get('updated_at', 'N/A')}")


def add_position(code: str, cost: float, quantity: int, name: str = ""):
    """添加持仓"""
    portfolio = load_portfolio()
    positions = portfolio.get("positions", [])
    
    # 检查是否已存在
    for pos in positions:
        if pos["code"] == code:
            print(f"持仓已存在: {code}，请使用 update 命令更新")
            return
    
    positions.append({
        "code": code,
        "name": name,
        "cost": cost,
        "quantity": quantity,
        "added_at": datetime.now().isoformat(),
    })
    
    portfolio["positions"] = positions
    save_portfolio(portfolio)
    print(f"已添加: {code} 成本{cost} 数量{quantity}")


def update_position(code: str, cost: float = None, quantity: int = None, name: str = None):
    """更新持仓"""
    portfolio = load_portfolio()
    positions = portfolio.get("positions", [])
    
    for pos in positions:
        if pos["code"] == code:
            if cost is not None:
                pos["cost"] = cost
            if quantity is not None:
                pos["quantity"] = quantity
            if name is not None:
                pos["name"] = name
            pos["updated_at"] = datetime.now().isoformat()
            save_portfolio(portfolio)
            print(f"已更新: {code}")
            return
    
    print(f"未找到持仓: {code}")


def remove_position(code: str):
    """删除持仓"""
    portfolio = load_portfolio()
    positions = portfolio.get("positions", [])
    
    new_positions = [p for p in positions if p["code"] != code]
    
    if len(new_positions) == len(positions):
        print(f"未找到持仓: {code}")
        return
    
    portfolio["positions"] = new_positions
    save_portfolio(portfolio)
    print(f"已删除: {code}")


def analyze_portfolio():
    """分析所有持仓"""
    portfolio = load_portfolio()
    positions = portfolio.get("positions", [])
    
    if not positions:
        print("暂无持仓记录")
        return
    
    print("=" * 70)
    print(f"持仓分析 - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 70)
    
    total_cost = 0
    total_value = 0
    
    results = []
    
    for pos in positions:
        code = pos["code"]
        result = analyze_stock(code, with_minute=True)
        
        if "error" in result:
            print(f"\n{code}: {result['error']}")
            continue
        
        # 更新持仓名称
        if not pos.get("name") and result.get("name"):
            pos["name"] = result["name"]
        
        realtime = result["realtime"]
        cost = pos["cost"]
        qty = pos["quantity"]
        
        cost_value = cost * qty
        market_value = realtime["price"] * qty
        pnl = market_value - cost_value
        pnl_pct = (realtime["price"] / cost - 1) * 100
        
        total_cost += cost_value
        total_value += market_value
        
        print(format_realtime(realtime))
        print(f"\n【持仓盈亏】")
        print(f"  成本: {cost:.3f}  持仓: {qty}股")
        print(f"  成本市值: {cost_value:.0f}  当前市值: {market_value:.0f}")
        print(f"  盈亏: {pnl:+.0f} ({pnl_pct:+.2f}%)")
        
        if "minute_analysis" in result:
            print(format_minute_analysis(result["minute_analysis"], result["name"]))
        
        print()
        results.append({
            "position": pos,
            "result": result,
            "pnl": pnl,
            "pnl_pct": pnl_pct,
        })
    
    # 汇总
    print("=" * 70)
    print("【持仓汇总】")
    print(f"  总成本: {total_cost:.0f} 元")
    print(f"  总市值: {total_value:.0f} 元")
    print(f"  总盈亏: {total_value - total_cost:+.0f} 元 ({(total_value/total_cost-1)*100:+.2f}%)")
    
    # 保存更新后的名称
    save_portfolio(portfolio)
    
    return results


def main():
    parser = argparse.ArgumentParser(description="A股持仓管理")
    subparsers = parser.add_subparsers(dest="command", help="命令")
    
    # show
    subparsers.add_parser("show", help="显示持仓")
    
    # add
    add_parser = subparsers.add_parser("add", help="添加持仓")
    add_parser.add_argument("code", help="股票代码")
    add_parser.add_argument("--cost", "-c", type=float, required=True, help="成本价")
    add_parser.add_argument("--qty", "-q", type=int, required=True, help="持仓数量")
    add_parser.add_argument("--name", "-n", default="", help="股票名称")
    
    # update
    update_parser = subparsers.add_parser("update", help="更新持仓")
    update_parser.add_argument("code", help="股票代码")
    update_parser.add_argument("--cost", "-c", type=float, help="成本价")
    update_parser.add_argument("--qty", "-q", type=int, help="持仓数量")
    update_parser.add_argument("--name", "-n", help="股票名称")
    
    # remove
    remove_parser = subparsers.add_parser("remove", help="删除持仓")
    remove_parser.add_argument("code", help="股票代码")
    
    # analyze
    subparsers.add_parser("analyze", help="持仓分析")
    
    args = parser.parse_args()
    
    if args.command == "show":
        show_portfolio()
    elif args.command == "add":
        add_position(args.code, args.cost, args.qty, args.name)
    elif args.command == "update":
        update_position(args.code, args.cost, args.qty, args.name)
    elif args.command == "remove":
        remove_position(args.code)
    elif args.command == "analyze":
        analyze_portfolio()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
