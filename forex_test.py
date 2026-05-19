#!/usr/bin/env python3
"""外汇自动测试脚本"""

import sys
sys.path.insert(0, '/Users/xiaoling/.hermes/workspace/auto_trading')

from forex_api import ForexAPI
from signal_system import SignalSystem
from risk_control import RiskControl
import json
from datetime import datetime

def run_forex_test():
    """运行外汇测试"""
    
    api = ForexAPI()
    sig = SignalSystem()
    rc = RiskControl(initial_balance=525)  # 老板外汇账户525美元
    
    symbols = ["EURUSD", "GBPUSD", "AUDUSD", "XAUUSD", "XAGUSD"]
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "type": "forex",
        "signals": [],
        "summary": {
            "total_signals": 0,
            "max_score": 0,
            "approved_count": 0
        }
    }
    
    print(f"\n{'='*50}")
    print(f"外汇自动交易测试")
    print(f"{'='*50}")
    
    # 扫描信号
    for symbol in symbols:
        try:
            print(f"\n扫描 {symbol}...")
            klines = api.get_klines(symbol, "1h", 100)
            
            if len(klines) < 30:
                print(f"  数据不足: {len(klines)}条")
                continue
            
            signal = sig.generate_signal(symbol, klines)
            
            if signal:
                results["signals"].append({
                    "symbol": symbol,
                    "direction": signal.direction,
                    "score": signal.score,
                    "entry": signal.entry,
                    "stop_loss": signal.stop_loss,
                    "take_profit": signal.take_profit,
                    "reason": signal.reason
                })
                
                # 风控检查
                risk = rc.check_risk(
                    symbol=signal.symbol,
                    direction=signal.direction,
                    entry=signal.entry,
                    stop_loss=signal.stop_loss,
                    take_profit=signal.take_profit
                )
                
                print(f"  ✓ 信号: {signal.direction} 分数={signal.score}")
                print(f"    入场: {signal.entry:.4f}")
                print(f"    止损: {signal.stop_loss:.4f}")
                print(f"    止盈: {signal.take_profit:.4f}")
                print(f"    风控通过: {risk.approved}")
                
                if risk.approved:
                    results["summary"]["approved_count"] += 1
                
                if signal.score > results["summary"]["max_score"]:
                    results["summary"]["max_score"] = signal.score
            else:
                print(f"  无信号")
        except Exception as e:
            print(f"  错误: {e}")
    
    results["summary"]["total_signals"] = len(results["signals"])
    
    # 保存结果
    output_path = "/Users/xiaoling/.hermes/workspace/auto_trading/forex_test_results.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # 输出摘要
    print(f"\n{'='*50}")
    print(f"测试完成")
    print(f"{'='*50}")
    print(f"信号数量: {results['summary']['total_signals']}")
    print(f"最高分数: {results['summary']['max_score']}")
    print(f"风控通过: {results['summary']['approved_count']}")
    print(f"{'='*50}\n")
    
    return results

if __name__ == "__main__":
    run_forex_test()
