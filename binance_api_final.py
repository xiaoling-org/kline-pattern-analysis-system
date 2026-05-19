"""
币安Testnet API封装 - 自动化交易系统核心模块
包含REST API和模拟WebSocket实时数据功能
"""

import requests
import json
import logging
import threading
import time
from datetime import datetime
from typing import Optional, Callable

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 币安Testnet配置
BASE_URL = "https://testnet.binance.vision/api/v3"


class BinanceAPI:
    """币安Testnet API客户端"""

    def __init__(self):
        self.session = requests.Session()
        self.positions = {}  # 模拟持仓
        self.orders = []  # 订单历史
        self.balance = 10000  # 初始余额USDT
        self.polling_threads = {}  # 轮询线程
        self.polling_callbacks = {}  # 轮询回调函数
        self.polling_active = {}  # 轮询状态

    def get_price(self, symbol: str) -> float:
        """获取当前价格"""
        try:
            url = f"{BASE_URL}/ticker/price"
            params = {"symbol": symbol.upper()}
            resp = self.session.get(url, params=params, timeout=10)
            data = resp.json()
            price = float(data["price"])
            logger.info(f"{symbol} 价格: {price}")
            return price
        except Exception as e:
            logger.error(f"获取价格失败: {e}")
            return 0.0

    def get_klines(self, symbol: str, interval: str = "1h", limit: int = 100) -> list:
        """获取K线数据"""
        try:
            url = f"{BASE_URL}/klines"
            params = {
                "symbol": symbol.upper(),
                "interval": interval,
                "limit": limit
            }
            resp = self.session.get(url, params=params, timeout=10)
            data = resp.json()

            klines = []
            for k in data:
                klines.append({
                    "time": k[0],
                    "open": float(k[1]),
                    "high": float(k[2]),
                    "low": float(k[3]),
                    "close": float(k[4]),
                    "volume": float(k[5])
                })
            logger.info(f"获取 {symbol} {interval} K线 {len(klines)} 条")
            return klines
        except Exception as e:
            logger.error(f"获取K线失败: {e}")
            return []

    def place_order(self, symbol: str, side: str, quantity: float,
                    price: Optional[float] = None) -> dict:
        """下单（模拟）"""
        try:
            current_price = self.get_price(symbol)

            # 模拟订单
            order = {
                "id": len(self.orders) + 1,
                "symbol": symbol.upper(),
                "side": side.upper(),  # BUY or SELL
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
                        (self.positions[symbol]["avg_price"] * self.positions[symbol]["quantity"] + cost)
                        / (self.positions[symbol]["quantity"] + quantity)
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
                    logger.warning(f"持仓不足: {self.positions[symbol]['quantity']} < {quantity}")
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

    def get_positions(self) -> list:
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

    def get_orders(self) -> list:
        """查询订单历史"""
        return self.orders

    def _price_polling_worker(self, symbol: str, callback: Callable, interval: float = 1.0):
        """价格轮询工作线程"""
        symbol_upper = symbol.upper()
        
        while self.polling_active.get(symbol_upper, False):
            try:
                price = self.get_price(symbol)
                if price > 0:
                    callback(price)
            except Exception as e:
                logger.error(f"轮询价格失败: {e}")
            
            time.sleep(interval)

    def subscribe_price(self, symbol: str, callback: Callable, interval: float = 1.0) -> bool:
        """订阅实时价格（使用轮询模拟）"""
        try:
            symbol_upper = symbol.upper()
            
            # 检查是否已经在订阅
            if symbol_upper in self.polling_active and self.polling_active[symbol_upper]:
                logger.warning(f"{symbol} 已经在订阅中")
                return False
            
            # 保存回调函数
            self.polling_callbacks[symbol_upper] = callback
            self.polling_active[symbol_upper] = True
            
            # 创建轮询线程
            polling_thread = threading.Thread(
                target=self._price_polling_worker,
                args=(symbol, callback, interval)
            )
            polling_thread.daemon = True
            polling_thread.start()
            
            self.polling_threads[symbol_upper] = polling_thread
            logger.info(f"已订阅 {symbol} 实时价格（轮询间隔: {interval}秒）")
            return True
            
        except Exception as e:
            logger.error(f"订阅实时价格失败: {e}")
            return False

    def unsubscribe_price(self, symbol: str) -> bool:
        """取消订阅实时价格"""
        try:
            symbol_upper = symbol.upper()
            
            if symbol_upper in self.polling_active:
                # 停止轮询
                self.polling_active[symbol_upper] = False
                
                # 等待线程结束
                if symbol_upper in self.polling_threads:
                    self.polling_threads[symbol_upper].join(timeout=2)
                    del self.polling_threads[symbol_upper]
                
                # 清理回调函数
                if symbol_upper in self.polling_callbacks:
                    del self.polling_callbacks[symbol_upper]
                
                del self.polling_active[symbol_upper]
                
                logger.info(f"已取消订阅 {symbol} 实时价格")
                return True
            else:
                logger.warning(f"{symbol} 未在订阅中")
                return False
                
        except Exception as e:
            logger.error(f"取消订阅失败: {e}")
            return False

    def close_all_connections(self):
        """关闭所有连接"""
        symbols = list(self.polling_active.keys())
        for symbol in symbols:
            self.unsubscribe_price(symbol)
        
        logger.info("已关闭所有连接")


# 测试代码
if __name__ == "__main__":
    api = BinanceAPI()

    print("=== 测试币安Testnet API ===")
    
    # 测试获取价格
    print("1. 测试获取价格...")
    price = api.get_price("BTCUSDT")
    print(f"   BTCUSDT价格: {price}")

    # 测试获取K线
    print("2. 测试获取K线...")
    klines = api.get_klines("BTCUSDT", "1h", 5)
    print(f"   获取到{len(klines)}条K线数据")

    # 测试下单
    print("3. 测试下单...")
    order = api.place_order("BTCUSDT", "BUY", 0.001)
    print(f"   下单结果: {order}")

    # 测试持仓
    print("4. 测试持仓...")
    positions = api.get_positions()
    print(f"   持仓: {positions}")
    print(f"   余额: {api.get_balance()}")

    # 测试模拟WebSocket实时价格
    print("5. 测试模拟WebSocket实时价格...")
    
    received_prices = []
    
    def price_callback(price):
        print(f"   实时价格回调: {price}")
        received_prices.append(price)
    
    # 订阅实时价格
    if api.subscribe_price("BTCUSDT", price_callback, interval=0.5):
        print("   模拟WebSocket订阅成功，等待3秒接收实时数据...")
        time.sleep(3)
        
        print(f"   共收到 {len(received_prices)} 条实时价格")
        
        # 取消订阅
        api.unsubscribe_price("BTCUSDT")
        print("   已取消订阅")
    
    print("=== 测试完成 ===")