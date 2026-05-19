#!/usr/bin/env python3
"""
币安Testnet API完整测试脚本
"""

import sys
import time
from binance_api import BinanceAPI

def test_all_functions():
    """测试所有API功能"""
    print("=" * 60)
    print("币安Testnet API完整测试")
    print("=" * 60)
    
    api = BinanceAPI()
    
    # 1. 测试获取价格
    print("\n1. 测试获取价格功能")
    print("-" * 40)
    symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]
    for symbol in symbols:
        price = api.get_price(symbol)
        print(f"   {symbol}: {price}")
        if price <= 0:
            print(f"   ⚠️ 警告: {symbol} 价格获取失败")
    
    # 2. 测试获取K线
    print("\n2. 测试获取K线功能")
    print("-" * 40)
    intervals = ["1m", "5m", "1h"]
    for interval in intervals:
        klines = api.get_klines("BTCUSDT", interval, 3)
        print(f"   BTCUSDT {interval} K线: {len(klines)} 条")
        if klines:
            print(f"   最新K线: 开={klines[-1]['open']}, 高={klines[-1]['high']}, 低={klines[-1]['low']}, 收={klines[-1]['close']}")
    
    # 3. 测试下单功能
    print("\n3. 测试下单功能")
    print("-" * 40)
    
    # 初始余额
    initial_balance = api.get_balance()
    print(f"   初始余额: {initial_balance} USDT")
    
    # 买入测试
    buy_order = api.place_order("BTCUSDT", "BUY", 0.001)
    print(f"   买入订单: {buy_order}")
    
    # 检查余额变化
    balance_after_buy = api.get_balance()
    print(f"   买入后余额: {balance_after_buy} USDT")
    
    # 4. 测试持仓查询
    print("\n4. 测试持仓查询功能")
    print("-" * 40)
    positions = api.get_positions()
    print(f"   当前持仓: {len(positions)} 个")
    for pos in positions:
        print(f"   {pos['symbol']}: 数量={pos['quantity']}, 均价={pos['avg_price']}, 现价={pos['current_price']}, 盈亏={pos['pnl']}")
    
    # 5. 测试卖出功能
    print("\n5. 测试卖出功能")
    print("-" * 40)
    if positions:
        sell_order = api.place_order("BTCUSDT", "SELL", 0.001)
        print(f"   卖出订单: {sell_order}")
        
        balance_after_sell = api.get_balance()
        print(f"   卖出后余额: {balance_after_sell} USDT")
        
        # 检查最终持仓
        final_positions = api.get_positions()
        print(f"   最终持仓: {len(final_positions)} 个")
    
    # 6. 测试订单历史
    print("\n6. 测试订单历史功能")
    print("-" * 40)
    orders = api.get_orders()
    print(f"   订单历史: {len(orders)} 笔")
    for i, order in enumerate(orders[-3:]):  # 显示最近3笔
        print(f"   订单{i+1}: {order['symbol']} {order['side']} {order['quantity']} @ {order['price']}")
    
    # 7. 测试实时价格订阅（模拟WebSocket）
    print("\n7. 测试实时价格订阅功能")
    print("-" * 40)
    
    price_updates = []
    
    def price_callback(price):
        price_updates.append(price)
        print(f"   价格更新: {price}")
    
    # 订阅实时价格
    if api.subscribe_price("BTCUSDT", price_callback, interval=0.3):
        print("   ✅ 实时价格订阅成功")
        print("   等待2秒接收价格更新...")
        time.sleep(2)
        
        print(f"   共收到 {len(price_updates)} 次价格更新")
        
        # 取消订阅
        api.unsubscribe_price("BTCUSDT")
        print("   ✅ 已取消订阅")
    else:
        print("   ❌ 实时价格订阅失败")
    
    # 8. 测试错误处理
    print("\n8. 测试错误处理功能")
    print("-" * 40)
    
    # 测试无效交易对
    invalid_price = api.get_price("INVALIDPAIR")
    print(f"   无效交易对价格: {invalid_price} (应为0.0)")
    
    # 测试余额不足
    large_order = api.place_order("BTCUSDT", "BUY", 1000)
    print(f"   大额订单结果: {large_order.get('status', 'unknown')} (应失败)")
    
    # 9. 清理和总结
    print("\n9. 测试总结")
    print("-" * 40)
    
    # 关闭所有连接
    api.close_all_connections()
    print("   ✅ 所有连接已关闭")
    
    final_balance = api.get_balance()
    print(f"   最终余额: {final_balance} USDT")
    
    # 性能统计
    total_orders = len(api.get_orders())
    total_positions = len(api.get_positions())
    
    print(f"\n📊 测试统计:")
    print(f"   • 总订单数: {total_orders}")
    print(f"   • 总持仓数: {total_positions}")
    print(f"   • 余额变化: {final_balance - initial_balance:.4f} USDT")
    
    print("\n" + "=" * 60)
    print("测试完成 ✅")
    print("=" * 60)

if __name__ == "__main__":
    try:
        test_all_functions()
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)