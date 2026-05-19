#!/usr/bin/env python3
"""
实时价格监控 - 获取最新市场价格
"""

import sys
sys.path.insert(0, '/Users/xiaoling/.hermes/workspace/auto_trading')

from binance_api import BinanceAPI
from forex_api import ForexAPI
import json
from datetime import datetime

def get_all_prices():
    """获取所有监控标的的实时价格"""
    
    crypto_api = BinanceAPI()
    forex_api = ForexAPI()
    
    prices = {
        "timestamp": datetime.now().isoformat(),
        "crypto": {},
        "forex": {}
    }
    
    # 加密货币价格
    crypto_symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT"]
    print("获取加密货币价格...")
    for symbol in crypto_symbols:
        try:
            price = crypto_api.get_price(symbol)
            prices["crypto"][symbol] = {
                "price": price,
                "change_24h": 0,  # 可以添加24小时变化
                "volume": 0
            }
            print(f"  {symbol}: {price}")
        except Exception as e:
            print(f"  {symbol}: 获取失败")
    
    # 外汇价格
    forex_symbols = ["EURUSD", "GBPUSD", "AUDUSD", "XAUUSD", "XAGUSD"]
    print("\n获取外汇价格...")
    for symbol in forex_symbols:
        try:
            price = forex_api.get_price(symbol)
            prices["forex"][symbol] = {
                "price": price,
                "change_24h": 0
            }
            print(f"  {symbol}: {price}")
        except Exception as e:
            print(f"  {symbol}: 获取失败")
    
    # 保存价格数据
    with open("/Users/xiaoling/.hermes/workspace/auto_trading/prices_data.json", "w") as f:
        json.dump(prices, f, indent=2)
    
    print(f"\n✓ 价格数据已更新")
    return prices

if __name__ == "__main__":
    get_all_prices()
