#!/usr/bin/env python3
"""
Telegram通知模块 - 实时推送交易系统消息
"""

import requests
import json
from datetime import datetime

# Telegram Bot配置
BOT_TOKEN = "YOUR_BOT_TOKEN"  # 需要从config中读取
CHAT_ID = "YOUR_CHAT_ID"  # 老板的Telegram ID

def send_message(text):
    """发送Telegram消息"""
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {
            "chat_id": CHAT_ID,
            "text": text,
            "parse_mode": "Markdown"
        }
        response = requests.post(url, data=data, timeout=10)
        return response.json()
    except Exception as e:
        print(f"发送失败: {e}")
        return None

def notify_test_complete(test_type, results):
    """测试完成通知"""
    message = f"""
📊 **{test_type}测试完成**

时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
信号数量: {results['summary']['total_signals']}
最高分数: {results['summary']['max_score']}
风控通过: {results['summary']['approved_count']}

详情查看: http://localhost:8080/dashboard.html
"""
    return send_message(message)

def notify_signal_found(signal):
    """发现信号通知"""
    message = f"""
🎯 **发现交易信号**

标的: {signal['symbol']}
方向: {signal['direction']}
分数: {signal['score']}
入场: {signal['entry']}
止损: {signal['stop_loss']}
止盈: {signal['take_profit']}
理由: {signal['reason']}

⚠️ 请确认是否执行
"""
    return send_message(message)

def notify_trade_executed(trade):
    """交易执行通知"""
    message = f"""
✅ **交易已执行**

标的: {trade['symbol']}
方向: {trade['side']}
数量: {trade['quantity']}
价格: {trade['price']}
时间: {trade['time']}
"""
    return send_message(message)

def notify_stop_loss_triggered(position):
    """止损触发通知"""
    message = f"""
⚠️ **止损触发**

标的: {position['symbol']}
止损价: {position['stop_loss']}
当前价: {position['current_price']}
亏损: {position['pnl']}

建议立即处理！
"""
    return send_message(message)

def notify_take_profit_triggered(position):
    """止盈触发通知"""
    message = f"""
🎉 **止盈触发**

标的: {position['symbol']}
止盈价: {position['take_profit']}
当前价: {position['current_price']}
盈利: {position['pnl']}

建议考虑平仓！
"""
    return send_message(message)

def notify_daily_report(report):
    """每日报告通知"""
    message = f"""
📈 **每日交易报告**

日期: {report['date']}
总交易: {report['total_trades']}
盈利: {report['profit_trades']}
亏损: {report['loss_trades']}
胜率: {report['win_rate']:.1%}
总盈亏: {report['total_pnl']:.2f}

详情查看: http://localhost:8080/dashboard.html
"""
    return send_message(message)

def notify_system_error(error):
    """系统错误通知"""
    message = f"""
❌ **系统错误**

错误: {error['type']}
详情: {error['message']}
时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

请检查系统状态！
"""
    return send_message(message)

# 测试
if __name__ == "__main__":
    print("Telegram通知模块测试")
    
    # 测试发送
    test_message = """
🧪 **测试消息**

这是小墨交易系统的测试通知。
如果收到此消息，说明Telegram通知已配置成功。

时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    result = send_message(test_message)
    if result and result.get('ok'):
        print("✓ Telegram通知测试成功")
    else:
        print("✗ Telegram通知测试失败")
