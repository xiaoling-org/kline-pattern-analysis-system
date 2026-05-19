#!/bin/bash
# 小墨交易系统 - 一键启动脚本

echo "========================================"
echo "小墨自动交易系统 - 启动中..."
echo "========================================"

# 1. 更新数据
echo ""
echo "【1/4】更新数据..."
python3 ~/.hermes/workspace/auto_trading/sync_data.py

# 2. 获取实时价格
echo ""
echo "【2/4】获取实时价格..."
python3 ~/.hermes/workspace/auto_trading/price_monitor.py

# 3. 启动API服务器
echo ""
echo "【3/4】启动API服务器..."
cd ~/.hermes/workspace/auto_trading
python3 api_server.py &
API_PID=$!
echo "API服务器已启动 (PID: $API_PID)"

# 4. 启动Dashboard服务器
echo ""
echo "【4/4】启动Dashboard服务器..."
python3 -m http.server 8080 &
DASHBOARD_PID=$!
echo "Dashboard服务器已启动 (PID: $DASHBOARD_PID)"

# 保存PID
echo $API_PID > /tmp/trading_api.pid
echo $DASHBOARD_PID > /tmp/trading_dashboard.pid

echo ""
echo "========================================"
echo "✓ 系统启动完成！"
echo "========================================"
echo ""
echo "访问地址："
echo "  Dashboard: http://localhost:8080/dashboard.html"
echo "  API: http://localhost:5000/api/status"
echo ""
echo "停止系统："
echo "  kill $API_PID $DASHBOARD_PID"
echo ""
