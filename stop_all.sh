#!/bin/bash
# 小墨交易系统 - 停止脚本

echo "停止交易系统..."

if [ -f /tmp/trading_api.pid ]; then
    kill $(cat /tmp/trading_api.pid) 2>/dev/null
    rm /tmp/trading_api.pid
fi

if [ -f /tmp/trading_dashboard.pid ]; then
    kill $(cat /tmp/trading_dashboard.pid) 2>/dev/null
    rm /tmp/trading_dashboard.pid
fi

# 杀掉所有相关进程
pkill -f "api_server.py"
pkill -f "http.server 8080"

echo "✓ 系统已停止"
