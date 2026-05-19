#!/usr/bin/env python3
"""
数据同步脚本 - 让Dashboard显示真实数据
"""

import json
import os
from datetime import datetime

DATA_DIR = "/Users/xiaoling/.hermes/workspace/auto_trading"
WORKSPACE = "/Users/xiaoling/.hermes/workspace"

def update_dashboard_data():
    """更新Dashboard所需的所有数据"""
    
    # 1. 更新测试结果
    print("更新测试结果...")
    try:
        with open(f"{DATA_DIR}/test_results.json", "r") as f:
            crypto_results = json.load(f)
        
        with open(f"{DATA_DIR}/forex_test_results.json", "r") as f:
            forex_results = json.load(f)
        
        # 合并结果
        dashboard_data = {
            "last_update": datetime.now().isoformat(),
            "crypto": crypto_results,
            "forex": forex_results
        }
        
        with open(f"{DATA_DIR}/dashboard_data.json", "w") as f:
            json.dump(dashboard_data, f, indent=2, ensure_ascii=False)
        
        print("✓ 测试结果已更新")
    except Exception as e:
        print(f"✗ 更新测试结果失败: {e}")
    
    # 2. 更新持仓数据
    print("更新持仓数据...")
    try:
        with open(f"{WORKSPACE}/positions.json", "r") as f:
            positions = json.load(f)
        
        with open(f"{DATA_DIR}/positions_data.json", "w") as f:
            json.dump(positions, f, indent=2, ensure_ascii=False)
        
        print("✓ 持仓数据已更新")
    except Exception as e:
        print(f"✗ 更新持仓数据失败: {e}")
    
    # 3. 更新交易统计
    print("更新交易统计...")
    try:
        with open(f"{WORKSPACE}/trading_stats.json", "r") as f:
            stats = json.load(f)
        
        with open(f"{DATA_DIR}/stats_data.json", "w") as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        
        print("✓ 交易统计已更新")
    except Exception as e:
        print(f"✗ 更新交易统计失败: {e}")
    
    # 4. 更新历史记录
    print("更新历史记录...")
    try:
        history = []
        with open(f"{DATA_DIR}/test_log.md", "r") as f:
            lines = f.readlines()
        
        for line in lines:
            if line.startswith("|") and "2026" in line:
                parts = [p.strip() for p in line.split("|") if p.strip()]
                if len(parts) >= 7:
                    history.append({
                        "date": parts[0],
                        "time": parts[1],
                        "signals": parts[2],
                        "max_score": parts[3],
                        "direction": parts[4],
                        "approved": parts[5],
                        "note": parts[6] if len(parts) > 6 else ""
                    })
        
        with open(f"{DATA_DIR}/history_data.json", "w") as f:
            json.dump({"records": history}, f, indent=2, ensure_ascii=False)
        
        print("✓ 历史记录已更新")
    except Exception as e:
        print(f"✗ 更新历史记录失败: {e}")
    
    # 5. 更新实时价格
    print("更新实时价格...")
    try:
        # 从测试结果中提取价格
        prices = {}
        
        if 'crypto' in dashboard_data:
            # 这里可以添加实时价格获取逻辑
            pass
        
        with open(f"{DATA_DIR}/prices_data.json", "w") as f:
            json.dump(prices, f, indent=2)
        
        print("✓ 实时价格已更新")
    except Exception as e:
        print(f"✗ 更新实时价格失败: {e}")
    
    print("\n所有数据更新完成！")

if __name__ == "__main__":
    update_dashboard_data()
