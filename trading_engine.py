"""
交易引擎 - 自动交易核心
"""

import time
import json
import logging
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

from binance_api import BinanceAPI
from signal_system import SignalSystem, Signal
from risk_control import RiskControl, RiskCheck

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TradingEngine:
    """交易引擎"""
    
    def __init__(self, symbols: List[str] = None, balance: float = 10000):
        self.symbols = symbols or ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
        self.api = BinanceAPI()
        self.signal_system = SignalSystem()
        self.risk_control = RiskControl(balance)
        
        self.running = False
        self.scan_interval = 300  # 5分钟扫描一次
        self.log_file = Path("~/.hermes/workspace/auto_trading/trades.json").expanduser()
        self.trades = self._load_trades()
    
    def _load_trades(self) -> List[Dict]:
        """加载交易记录"""
        if self.log_file.exists():
            with open(self.log_file, 'r') as f:
                return json.load(f)
        return []
    
    def _save_trade(self, trade: Dict):
        """保存交易记录"""
        self.trades.append(trade)
        with open(self.log_file, 'w') as f:
            json.dump(self.trades, f, indent=2, ensure_ascii=False)
    
    def scan_signals(self) -> List[Signal]:
        """扫描所有品种信号"""
        signals = []
        
        for symbol in self.symbols:
            try:
                klines = self.api.get_klines(symbol, "1h", 100)
                if not klines:
                    continue
                
                signal = self.signal_system.generate_signal(symbol, klines)
                if signal and signal.score >= 60:
                    signals.append(signal)
                    logger.info(f"📊 {symbol} 信号: {signal.direction} 分数={signal.score}")
            
            except Exception as e:
                logger.error(f"扫描{symbol}失败: {e}")
        
        # 按分数排序
        signals.sort(key=lambda s: s.score, reverse=True)
        return signals
    
    def execute_trade(self, signal: Signal) -> bool:
        """执行交易"""
        
        # 风控检查
        check: RiskCheck = self.risk_control.check_risk(
            signal.symbol, signal.direction, 
            signal.entry, signal.stop_loss, signal.take_profit
        )
        
        if not check.approved:
            logger.warning(f"❌ 风控拒绝: {check.reason}")
            return False
        
        # 执行下单
        side = "BUY" if signal.direction == "LONG" else "SELL"
        order = self.api.place_order(signal.symbol, side, check.position_size)
        
        if order.get("status") == "failed":
            logger.error(f"下单失败: {order}")
            return False
        
        # 记录交易
        trade = {
            "time": datetime.now().isoformat(),
            "symbol": signal.symbol,
            "direction": signal.direction,
            "entry": signal.entry,
            "stop_loss": signal.stop_loss,
            "take_profit": signal.take_profit,
            "quantity": check.position_size,
            "score": signal.score,
            "reason": signal.reason,
            "order_id": order.get("id"),
            "status": "open"
        }
        
        self._save_trade(trade)
        self.risk_control.add_position(signal.symbol, signal.direction, 
                                        check.position_size, signal.entry)
        
        logger.info(f"✅ 交易执行: {signal.symbol} {signal.direction} @ {signal.entry}")
        return True
    
    def check_open_positions(self):
        """检查持仓止损止盈"""
        positions = self.api.get_positions()
        
        for pos in positions:
            symbol = pos["symbol"]
            current_price = pos["current_price"]
            
            # 找对应交易记录
            for trade in reversed(self.trades):
                if trade["symbol"] == symbol and trade["status"] == "open":
                    # 检查止损
                    if trade["direction"] == "LONG" and current_price <= trade["stop_loss"]:
                        self._close_position(trade, "STOP_LOSS", current_price)
                    elif trade["direction"] == "SHORT" and current_price >= trade["stop_loss"]:
                        self._close_position(trade, "STOP_LOSS", current_price)
                    # 检查止盈
                    elif trade["direction"] == "LONG" and current_price >= trade["take_profit"]:
                        self._close_position(trade, "TAKE_PROFIT", current_price)
                    elif trade["direction"] == "SHORT" and current_price <= trade["take_profit"]:
                        self._close_position(trade, "TAKE_PROFIT", current_price)
                    break
    
    def _close_position(self, trade: Dict, reason: str, price: float):
        """平仓"""
        side = "SELL" if trade["direction"] == "LONG" else "BUY"
        self.api.place_order(trade["symbol"], side, trade["quantity"])
        
        # 计算盈亏
        if trade["direction"] == "LONG":
            pnl = (price - trade["entry"]) * trade["quantity"]
        else:
            pnl = (trade["entry"] - price) * trade["quantity"]
        
        trade["status"] = reason
        trade["close_price"] = price
        trade["pnl"] = pnl
        trade["close_time"] = datetime.now().isoformat()
        
        self._save_trade(trade)
        self.risk_control.remove_position(trade["symbol"])
        self.risk_control.update_balance(self.api.get_balance())
        
        logger.info(f"🎯 平仓: {trade['symbol']} {reason} PnL={pnl:.2f}")
    
    def run(self):
        """主循环"""
        logger.info("🚀 交易引擎启动")
        self.running = True
        
        while self.running:
            try:
                # 扫描信号
                signals = self.scan_signals()
                
                # 执行最高分信号
                if signals:
                    self.execute_trade(signals[0])
                
                # 检查持仓
                self.check_open_positions()
                
                # 更新状态
                status = self.risk_control.get_status()
                logger.info(f"💰 余额: {status['balance']:.2f} | 回撤: {status['drawdown']}")
                
                # 等待
                time.sleep(self.scan_interval)
                
            except KeyboardInterrupt:
                logger.info("停止交易")
                self.running = False
            except Exception as e:
                logger.error(f"运行错误: {e}")
                time.sleep(60)
    
    def stop(self):
        """停止"""
        self.running = False


if __name__ == "__main__":
    engine = TradingEngine(
        symbols=["BTCUSDT", "ETHUSDT", "SOLUSDT"],
        balance=10000
    )
    engine.run()
