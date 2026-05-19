"""
推送系统 - Dashboard和Telegram通知
"""

import json
import requests
import logging
from datetime import datetime
from typing import Dict, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class PushSystem:
    """推送系统"""
    
    def __init__(self):
        self.dashboard_url = "http://127.0.0.1:8080/api/signals"
        self.log_file = Path("~/.hermes/workspace/auto_trading/notifications.json").expanduser()
    
    def to_dashboard(self, signal: Dict) -> bool:
        """推送到指挥中心Dashboard"""
        try:
            resp = requests.post(
                self.dashboard_url,
                json=signal,
                timeout=5
            )
            if resp.status_code == 200:
                logger.info("✅ Dashboard推送成功")
                return True
            logger.warning(f"Dashboard推送失败: {resp.status_code}")
            return False
        except Exception as e:
            logger.error(f"Dashboard推送异常: {e}")
            return False
    
    def to_telegram(self, message: str, bot_token: str = None, chat_id: str = None) -> bool:
        """推送到Telegram"""
        # 从配置读取
        config_file = Path("~/.hermes/workspace/auto_trading/config.json").expanduser()
        if config_file.exists():
            with open(config_file, 'r') as f:
                config = json.load(f)
                bot_token = bot_token or config.get("telegram_bot_token")
                chat_id = chat_id or config.get("telegram_chat_id")
        
        if not bot_token or not chat_id:
            logger.warning("Telegram配置缺失")
            return False
        
        try:
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            resp = requests.post(url, json={
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "HTML"
            }, timeout=10)
            
            if resp.status_code == 200:
                logger.info("✅ Telegram推送成功")
                return True
            return False
        except Exception as e:
            logger.error(f"Telegram推送异常: {e}")
            return False
    
    def format_signal_message(self, signal: Dict) -> str:
        """格式化信号消息"""
        direction_emoji = "🟢" if signal["direction"] == "LONG" else "🔴"
        return f"""
{direction_emoji} <b>交易信号</b>

品种: {signal['symbol']}
方向: {signal['direction']}
分数: {signal['score']}

入场: {signal['entry']:.4f}
止损: {signal['stop_loss']:.4f}
止盈: {signal['take_profit']:.4f}

理由: {signal['reason']}
时间: {datetime.now().strftime('%H:%M:%S')}
"""
    
    def notify_trade(self, trade: Dict):
        """交易通知"""
        msg = self.format_signal_message(trade)
        self.to_telegram(msg)
        self.to_dashboard(trade)
    
    def notify_close(self, trade: Dict):
        """平仓通知"""
        pnl_emoji = "💰" if trade.get("pnl", 0) > 0 else "📉"
        msg = f"""
{pnl_emoji} <b>平仓通知</b>

品种: {trade['symbol']}
原因: {trade['status']}
盈亏: {trade.get('pnl', 0):.2f} USDT

时间: {datetime.now().strftime('%H:%M:%S')}
"""
        self.to_telegram(msg)


if __name__ == "__main__":
    push = PushSystem()
    print("推送系统初始化完成")
