"""
外汇API封装 - 使用yfinance获取外汇数据
"""

import yfinance as yf
import logging
from typing import List, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# 主要外汇对
FOREX_PAIRS = {
    "EURUSD": "EURUSD=X",
    "GBPUSD": "GBPUSD=X",
    "AUDUSD": "AUDUSD=X",
    "USDJPY": "USDJPY=X",
    "USDCAD": "USDCAD=X",
    "USDCHF": "USDCHF=X",
    "XAUUSD": "GC=F",  # 黄金
    "XAGUSD": "SI=F"   # 白银
}


class ForexAPI:
    """外汇API客户端"""
    
    def __init__(self):
        self.positions = {}
        self.orders = []
        self.balance = 525  # 初始525美元（老板实际外汇账户）
    
    def get_price(self, symbol: str) -> float:
        """获取当前价格"""
        try:
            ticker = yf.Ticker(FOREX_PAIRS.get(symbol, symbol))
            data = ticker.history(period="1d")
            if len(data) > 0:
                price = data["Close"].iloc[-1]
                logger.info(f"{symbol} 价格: {price}")
                return float(price)
            return 0.0
        except Exception as e:
            logger.error(f"获取价格失败: {e}")
            return 0.0
    
    def get_klines(self, symbol: str, interval: str = "1h", limit: int = 100) -> List[Dict]:
        """获取K线数据"""
        try:
            ticker = yf.Ticker(FOREX_PAIRS.get(symbol, symbol))
            
            # 转换interval格式
            period_map = {
                "1h": "1h",
                "4h": "1h",  # yfinance不支持4h，用1h代替
                "1d": "1d"
            }
            
            # 获取足够的历史数据
            period = "60d" if interval in ["1h", "4h"] else "200d"
            data = ticker.history(period=period, interval="1h")
            
            klines = []
            for idx, row in data.tail(limit).iterrows():
                klines.append({
                    "time": int(idx.timestamp() * 1000),
                    "open": float(row["Open"]),
                    "high": float(row["High"]),
                    "low": float(row["Low"]),
                    "close": float(row["Close"]),
                    "volume": float(row.get("Volume", 0))
                })
            
            logger.info(f"获取 {symbol} K线 {len(klines)} 条")
            return klines
        except Exception as e:
            logger.error(f"获取K线失败: {e}")
            return []
    
    def place_order(self, symbol: str, side: str, quantity: float,
                    price: Optional[float] = None) -> dict:
        """下单（模拟）"""
        try:
            current_price = self.get_price(symbol)
            
            order = {
                "id": len(self.orders) + 1,
                "symbol": symbol,
                "side": side.upper(),
                "quantity": quantity,
                "price": price or current_price,
                "status": "filled",
                "time": datetime.now().isoformat()
            }
            
            # 更新持仓和余额
            if side.upper() == "BUY":
                cost = order["price"] * quantity
                if cost > self.balance:
                    logger.warning(f"余额不足: {self.balance} < {cost}")
                    return {"status": "failed", "reason": "insufficient_balance"}
                
                self.balance -= cost
                if symbol in self.positions:
                    self.positions[symbol]["quantity"] += quantity
                    self.positions[symbol]["avg_price"] = (
                        (self.positions[symbol]["avg_price"] * 
                         (self.positions[symbol]["quantity"] - quantity) + cost)
                        / self.positions[symbol]["quantity"]
                    )
                else:
                    self.positions[symbol] = {
                        "quantity": quantity,
                        "avg_price": order["price"]
                    }
            else:  # SELL
                if symbol not in self.positions:
                    logger.warning(f"无持仓: {symbol}")
                    return {"status": "failed", "reason": "no_position"}
                
                if self.positions[symbol]["quantity"] < quantity:
                    logger.warning(f"持仓不足")
                    return {"status": "failed", "reason": "insufficient_position"}
                
                revenue = order["price"] * quantity
                self.balance += revenue
                self.positions[symbol]["quantity"] -= quantity
                
                if self.positions[symbol]["quantity"] == 0:
                    del self.positions[symbol]
            
            self.orders.append(order)
            logger.info(f"订单执行: {order}")
            return order
        except Exception as e:
            logger.error(f"下单失败: {e}")
            return {"status": "failed", "reason": str(e)}
    
    def get_positions(self) -> List[Dict]:
        """查询持仓"""
        positions = []
        for symbol, pos in self.positions.items():
            current_price = self.get_price(symbol)
            pnl = (current_price - pos["avg_price"]) * pos["quantity"]
            positions.append({
                "symbol": symbol,
                "quantity": pos["quantity"],
                "avg_price": pos["avg_price"],
                "current_price": current_price,
                "pnl": pnl
            })
        return positions
    
    def get_balance(self) -> float:
        """查询余额"""
        return self.balance


if __name__ == "__main__":
    api = ForexAPI()
    
    # 测试
    print("EURUSD 价格:", api.get_price("EURUSD"))
    print("XAUUSD 价格:", api.get_price("XAUUSD"))
    
    klines = api.get_klines("EURUSD", "1h", 10)
    print("K线数据:", len(klines), "条")
