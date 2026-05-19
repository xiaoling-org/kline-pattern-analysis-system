"""
风控系统 - 仓位管理与风险控制
"""

import logging
from typing import Dict, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class RiskCheck:
    """风控检查结果"""
    approved: bool
    position_size: float
    reason: str


class RiskControl:
    """风控系统"""
    
    def __init__(self, initial_balance: float = 10000):
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.max_risk_per_trade = 0.02  # 单笔最大风险2%
        self.max_total_position = 0.50   # 最大总仓位50%
        self.max_drawdown_warning = 0.10  # 回撤警告线10%
        self.max_drawdown_stop = 0.20     # 回撤停止线20%
        self.current_positions = {}       # 当前持仓
        self.trading_enabled = True       # 交易开关
    
    def update_balance(self, new_balance: float):
        """更新余额"""
        self.balance = new_balance
        
        # 检查回撤
        drawdown = (self.initial_balance - self.balance) / self.initial_balance
        
        if drawdown >= self.max_drawdown_stop:
            self.trading_enabled = False
            logger.warning(f"⚠️ 回撤超{self.max_drawdown_stop*100}%，停止交易")
        elif drawdown >= self.max_drawdown_warning:
            logger.warning(f"⚠️ 回撤达{self.max_drawdown_warning*100}%，注意风险")
    
    def calculate_position_size(self, entry: float, stop_loss: float) -> float:
        """计算仓位大小"""
        risk_amount = self.balance * self.max_risk_per_trade
        price_risk = abs(entry - stop_loss)
        
        if price_risk == 0:
            return 0
        
        position_size = risk_amount / price_risk
        return round(position_size, 6)
    
    def check_risk(self, symbol: str, direction: str, entry: float, 
                   stop_loss: float, take_profit: float) -> RiskCheck:
        """风控检查"""
        
        # 检查交易开关
        if not self.trading_enabled:
            return RiskCheck(False, 0, "交易已暂停（回撤过大）")
        
        # 检查止损合理性
        if direction == "LONG" and stop_loss >= entry:
            return RiskCheck(False, 0, "做多止损必须低于入场价")
        if direction == "SHORT" and stop_loss <= entry:
            return RiskCheck(False, 0, "做空止损必须高于入场价")
        
        # 计算仓位
        position_size = self.calculate_position_size(entry, stop_loss)
        
        # 检查总仓位
        current_exposure = sum(
            p["quantity"] * p["entry"] 
            for p in self.current_positions.values()
        )
        new_exposure = current_exposure + (position_size * entry)
        max_exposure = self.balance * self.max_total_position
        
        if new_exposure > max_exposure:
            return RiskCheck(False, 0, f"总仓位超限: {new_exposure:.2f} > {max_exposure:.2f}")
        
        # 检查盈亏比
        risk = abs(entry - stop_loss)
        reward = abs(take_profit - entry)
        risk_reward = reward / risk if risk > 0 else 0
        
        if risk_reward < 1.5:
            return RiskCheck(False, 0, f"盈亏比不足: {risk_reward:.2f} < 1.5")
        
        logger.info(f"✅ 风控通过: {symbol} {direction} 仓位={position_size} 盈亏比={risk_reward:.2f}")
        
        return RiskCheck(True, position_size, f"批准 | 盈亏比{risk_reward:.2f}")
    
    def add_position(self, symbol: str, direction: str, quantity: float, entry: float):
        """添加持仓"""
        self.current_positions[symbol] = {
            "direction": direction,
            "quantity": quantity,
            "entry": entry
        }
    
    def remove_position(self, symbol: str):
        """移除持仓"""
        if symbol in self.current_positions:
            del self.current_positions[symbol]
    
    def emergency_stop(self):
        """紧急停止"""
        self.trading_enabled = False
        logger.warning("🚨 紧急停止交易！")
    
    def get_status(self) -> Dict:
        """获取状态"""
        drawdown = (self.initial_balance - self.balance) / self.initial_balance
        return {
            "balance": self.balance,
            "drawdown": f"{drawdown*100:.2f}%",
            "trading_enabled": self.trading_enabled,
            "positions": len(self.current_positions)
        }


if __name__ == "__main__":
    rc = RiskControl(10000)
    print("风控系统初始化完成")
    print(rc.get_status())
