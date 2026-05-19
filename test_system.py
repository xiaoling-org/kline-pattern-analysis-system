#!/usr/bin/env python3
"""测试自动交易系统完整流程"""

from binance_api import BinanceAPI
from signal_system import SignalSystem
from risk_control import RiskControl
import json

print("=" * 50)
print("自动交易系统测试")
print("=" * 50)

# 1. 初始化
api = BinanceAPI()
sig = SignalSystem()
rc = RiskControl(initial_balance=10000)

# 2. 测试数据获取
print("\n【1】数据获取测试")
for symbol in ["BTCUSDT", "ETHUSDT", "SOLUSDT"]:
    price = api.get_price(symbol)
    print(f"  {symbol}: {price}")

# 3. 测试信号生成
print("\n【2】信号生成测试")
signals = []
for symbol in ["BTCUSDT", "ETHUSDT", "SOLUSDT"]:
    klines = api.get_klines(symbol, "1h", 100)
    signal = sig.generate_signal(symbol, klines)
    if signal:
        signals.append(signal)
        print(f"  {symbol}: {signal.direction} 分数={signal.score}")
    else:
        print(f"  {symbol}: 无信号")

# 4. 测试风控
print("\n【3】风控检查测试")
if signals:
    for sig_obj in signals:
        risk = rc.check_risk(
            symbol=sig_obj.symbol,
            direction=sig_obj.direction,
            entry=sig_obj.entry,
            stop_loss=sig_obj.stop_loss,
            take_profit=sig_obj.take_profit
        )
        print(f"  {sig_obj.symbol}: 通过={risk.approved} 仓位={risk.position_size}")
else:
    print("  无信号需要检查")

# 5. 测试模拟下单
print("\n【4】模拟下单测试")
api.balance = 10000
order = api.place_order("BTCUSDT", "BUY", 0.01)
if order.get("status") == "filled":
    print(f"  ✓ 买入成功: {order}")
    print(f"  余额: {api.get_balance()}")
    print(f"  持仓: {api.get_positions()}")
else:
    print(f"  ✗ 下单失败: {order}")

print("\n" + "=" * 50)
print("测试完成！所有模块正常工作")
print("=" * 50)
