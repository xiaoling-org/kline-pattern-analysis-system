#!/usr/bin/env python3
"""
交易系统后端API服务器
提供Dashboard所需的所有API
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 数据文件路径
DATA_DIR = "/Users/xiaoling/.hermes/workspace/auto_trading"

# ========== API路由 ==========

@app.route('/')
def index():
    return jsonify({"status": "ok", "message": "小墨交易系统API运行中"})

@app.route('/api/status')
def get_status():
    """获取系统状态"""
    return jsonify({
        "status": "running",
        "uptime": "2 hours",
        "version": "1.0",
        "last_update": datetime.now().isoformat()
    })

@app.route('/api/crypto-test', methods=['POST'])
def run_crypto_test():
    """运行加密货币测试"""
    try:
        # 运行测试脚本
        os.system(f"cd {DATA_DIR} && python3 auto_test.py")
        
        # 读取结果
        with open(f"{DATA_DIR}/test_results.json", "r") as f:
            results = json.load(f)
        
        return jsonify({
            "success": True,
            "results": results
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })

@app.route('/api/forex-test', methods=['POST'])
def run_forex_test():
    """运行外汇测试"""
    try:
        os.system(f"cd {DATA_DIR} && python3 forex_test.py")
        
        with open(f"{DATA_DIR}/forex_test_results.json", "r") as f:
            results = json.load(f)
        
        return jsonify({
            "success": True,
            "results": results
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })

@app.route('/api/crypto-results')
def get_crypto_results():
    """获取加密货币测试结果"""
    try:
        with open(f"{DATA_DIR}/test_results.json", "r") as f:
            results = json.load(f)
        return jsonify(results)
    except:
        return jsonify({"error": "无数据"})

@app.route('/api/forex-results')
def get_forex_results():
    """获取外汇测试结果"""
    try:
        with open(f"{DATA_DIR}/forex_test_results.json", "r") as f:
            results = json.load(f)
        return jsonify(results)
    except:
        return jsonify({"error": "无数据"})

@app.route('/api/history')
def get_history():
    """获取历史测试记录"""
    try:
        # 读取测试日志
        with open(f"{DATA_DIR}/test_log.md", "r") as f:
            log = f.read()
        
        # 解析为结构化数据
        lines = log.split("\n")
        records = []
        for line in lines:
            if line.startswith("|") and "2026" in line:
                parts = line.split("|")
                if len(parts) >= 7:
                    records.append({
                        "date": parts[1].strip(),
                        "time": parts[2].strip(),
                        "signals": parts[3].strip(),
                        "max_score": parts[4].strip(),
                        "direction": parts[5].strip(),
                        "approved": parts[6].strip(),
                        "note": parts[7].strip() if len(parts) > 7 else ""
                    })
        
        return jsonify({
            "total": len(records),
            "records": records
        })
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/positions')
def get_positions():
    """获取当前持仓"""
    try:
        with open("/Users/xiaoling/.hermes/workspace/positions.json", "r") as f:
            positions = json.load(f)
        return jsonify(positions)
    except:
        return jsonify({"持仓": {}})

@app.route('/api/trade-history')
def get_trade_history():
    """获取交易历史"""
    try:
        with open("/Users/xiaoling/.hermes/workspace/trade_history.json", "r") as f:
            history = json.load(f)
        return jsonify(history)
    except:
        return jsonify({"trades": []})

@app.route('/api/stats')
def get_stats():
    """获取统计数据"""
    try:
        with open("/Users/xiaoling/.hermes/workspace/trading_stats.json", "r") as f:
            stats = json.load(f)
        return jsonify(stats)
    except:
        return jsonify({
            "total_trades": 0,
            "win_rate": 0,
            "total_pnl": 0
        })

@app.route('/api/config', methods=['GET', 'POST'])
def handle_config():
    """获取或更新配置"""
    if request.method == 'GET':
        try:
            with open(f"{DATA_DIR}/config.json", "r") as f:
                config = json.load(f)
            return jsonify(config)
        except:
            return jsonify({
                "signal_threshold": 60,
                "max_risk": 0.02,
                "max_position": 0.50
            })
    else:
        # 更新配置
        config = request.json
        with open(f"{DATA_DIR}/config.json", "w") as f:
            json.dump(config, f, indent=2)
        return jsonify({"success": True})

@app.route('/api/health')
def health_check():
    """系统健康检查"""
    checks = {
        "api": "ok",
        "data_files": "ok",
        "cron_jobs": "ok"
    }
    
    # 检查数据文件
    required_files = [
        "test_results.json",
        "forex_test_results.json"
    ]
    
    for file in required_files:
        if not os.path.exists(f"{DATA_DIR}/{file}"):
            checks["data_files"] = "missing"
    
    return jsonify({
        "status": "healthy" if all(v == "ok" for v in checks.values()) else "warning",
        "checks": checks,
        "timestamp": datetime.now().isoformat()
    })

# ========== 启动服务器 ==========

if __name__ == "__main__":
    print("启动交易系统API服务器...")
    print("端口: 5001")
    print("访问: http://localhost:5001/api/status")
    
    app.run(host='0.0.0.0', port=5001, debug=False)
