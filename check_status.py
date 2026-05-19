#!/usr/bin/env python3
"""
系统状态检查 - 检查所有组件是否正常运行
"""

import requests
import json
import os

def check_system():
    print("=" * 60)
    print("小墨交易系统 - 状态检查")
    print("=" * 60)
    
    checks = []
    
    # 1. 检查API服务器
    print("\n【1】API服务器")
    try:
        response = requests.get("http://localhost:5000/api/status", timeout=5)
        if response.status_code == 200:
            print("  ✓ 运行正常")
            checks.append(True)
        else:
            print("  ✗ 响应异常")
            checks.append(False)
    except:
        print("  ✗ 无法连接")
        checks.append(False)
    
    # 2. 检查Dashboard服务器
    print("\n【2】Dashboard服务器")
    try:
        response = requests.get("http://localhost:8080/dashboard.html", timeout=5)
        if response.status_code == 200:
            print("  ✓ 运行正常")
            checks.append(True)
        else:
            print("  ✗ 响应异常")
            checks.append(False)
    except:
        print("  ✗ 无法连接")
        checks.append(False)
    
    # 3. 检查数据文件
    print("\n【3】数据文件")
    required_files = [
        "test_results.json",
        "forex_test_results.json",
        "dashboard_data.json",
        "positions_data.json",
        "prices_data.json",
        "config.json"
    ]
    
    data_dir = "/Users/xiaoling/.hermes/workspace/auto_trading"
    all_exist = True
    for file in required_files:
        path = f"{data_dir}/{file}"
        if os.path.exists(path):
            print(f"  ✓ {file}")
        else:
            print(f"  ✗ {file} 不存在")
            all_exist = False
    checks.append(all_exist)
    
    # 4. 检查cron jobs
    print("\n【4】定时任务")
    try:
        import subprocess
        result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
        if "auto_test.py" in result.stdout:
            print("  ✓ 加密货币测试任务已配置")
            checks.append(True)
        else:
            print("  ✗ 未配置定时任务")
            checks.append(False)
    except:
        print("  ✗ 无法检查")
        checks.append(False)
    
    # 总结
    print("\n" + "=" * 60)
    if all(checks):
        print("✓ 系统状态：完美")
    else:
        print(f"⚠ 系统状态：{sum(checks)}/{len(checks)} 项正常")
    print("=" * 60)
    
    return all(checks)

if __name__ == "__main__":
    check_system()
