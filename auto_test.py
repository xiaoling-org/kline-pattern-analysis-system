#!/usr/bin/env python3
"""自动测试脚本 - 每天定时运行"""

import sys
sys.path.insert(0, '/Users/xiaoling/.hermes/workspace/auto_trading')

from binance_api import BinanceAPI
from signal_system import SignalSystem
from risk_control import RiskControl
import json
from datetime import datetime

def run_test():
    """运行测试并记录结果"""
    
    api = BinanceAPI()
    sig = SignalSystem()
    rc = RiskControl(initial_balance=10000)
    
    symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT"]
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "signals": [],
        "summary": {
            "total_signals": 0,
            "max_score": 0,
            "approved_count": 0
        }
    }
    
    # 扫描信号
    for symbol in symbols:
        try:
            klines = api.get_klines(symbol, "1h", 100)
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
                
                if risk.approved:
                    results["summary"]["approved_count"] += 1
                
                if signal.score > results["summary"]["max_score"]:
                    results["summary"]["max_score"] = signal.score
        except Exception as e:
            print(f"错误 {symbol}: {e}")
    
    results["summary"]["total_signals"] = len(results["signals"])
    
    # 保存结果
    output_path = "/Users/xiaoling/.hermes/workspace/auto_trading/test_results.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # 输出摘要
    print(f"\n{'='*50}")
    print(f"测试时间: {results['timestamp']}")
    print(f"{'='*50}")
    print(f"信号数量: {results['summary']['total_signals']}")
    print(f"最高分数: {results['summary']['max_score']}")
    print(f"风控通过: {results['summary']['approved_count']}")
    
    if results["signals"]:
        print(f"\n信号详情:")
        for s in results["signals"]:
            print(f"  {s['symbol']}: {s['direction']} 分数={s['score']}")
    else:
        print("\n无信号")
    
    print(f"{'='*50}\n")
    
    return results

if __name__ == "__main__":
    run_test()
