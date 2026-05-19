"""
信号系统 - 技术指标计算与交易信号生成
"""

import logging
from typing import Dict, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class Signal:
    """交易信号"""
    symbol: str
    direction: str  # LONG / SHORT
    score: int  # 0-100
    entry: float
    stop_loss: float
    take_profit: float
    reason: str


class SignalSystem:
    """信号系统"""
    
    def __init__(self):
        self.min_score = 60  # 最低信号分数
    
    def calculate_ma(self, prices: List[float], period: int) -> float:
        """计算均线"""
        if len(prices) < period:
            return 0
        return sum(prices[-period:]) / period
    
    def calculate_ema(self, prices: List[float], period: int) -> float:
        """计算EMA"""
        if len(prices) < period:
            return 0
        multiplier = 2 / (period + 1)
        ema = sum(prices[:period]) / period
        for price in prices[period:]:
            ema = (price - ema) * multiplier + ema
        return ema
    
    def calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """计算RSI"""
        if len(prices) < period + 1:
            return 50
        gains, losses = [], []
        for i in range(1, len(prices)):
            change = prices[i] - prices[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))
        
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        
        if avg_loss == 0:
            return 100
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))
    
    def calculate_macd(self, prices: List[float]) -> Dict[str, float]:
        """计算MACD"""
        ema12 = self.calculate_ema(prices, 12)
        ema26 = self.calculate_ema(prices, 26)
        macd = ema12 - ema26
        signal = macd * 0.2 + macd * 0.8  # 简化信号线
        histogram = macd - signal
        return {"macd": macd, "signal": signal, "histogram": histogram}
    
    def find_support_resistance(self, klines: List[Dict]) -> Dict[str, float]:
        """找支撑阻力位"""
        if len(klines) < 20:
            return {"support": 0, "resistance": 0}
        
        highs = [k["high"] for k in klines[-20:]]
        lows = [k["low"] for k in klines[-20:]]
        
        return {
            "support": min(lows),
            "resistance": max(highs)
        }
    
    def detect_candle_pattern(self, klines: List[Dict]) -> Optional[str]:
        """K线形态识别"""
        if len(klines) < 2:
            return None
        
        curr = klines[-1]
        prev = klines[-2]
        
        body_curr = abs(curr["close"] - curr["open"])
        body_prev = abs(prev["close"] - prev["open"])
        
        # 看涨吞没
        if prev["close"] < prev["open"] and curr["close"] > curr["open"]:
            if curr["close"] > prev["open"] and curr["open"] < prev["close"]:
                return "BULLISH_ENGULFING"
        
        # 看跌吞没
        if prev["close"] > prev["open"] and curr["close"] < curr["open"]:
            if curr["close"] < prev["open"] and curr["open"] > prev["close"]:
                return "BEARISH_ENGULFING"
        
        # 锤子线
        lower_wick = min(curr["open"], curr["close"]) - curr["low"]
        upper_wick = curr["high"] - max(curr["open"], curr["close"])
        if lower_wick > body_curr * 2 and upper_wick < body_curr * 0.5:
            return "HAMMER"
        
        # 倒锤子
        if upper_wick > body_curr * 2 and lower_wick < body_curr * 0.5:
            return "INVERTED_HAMMER"
        
        return None
    
    def generate_signal(self, symbol: str, klines: List[Dict]) -> Optional[Signal]:
        """生成交易信号"""
        if len(klines) < 30:
            logger.warning(f"{symbol} K线数据不足")
            return None
        
        closes = [k["close"] for k in klines]
        current_price = closes[-1]
        
        # 计算指标
        ma20 = self.calculate_ma(closes, 20)
        ma50 = self.calculate_ma(closes, 50)
        rsi = self.calculate_rsi(closes)
        macd = self.calculate_macd(closes)
        sr = self.find_support_resistance(klines)
        pattern = self.detect_candle_pattern(klines)
        
        # 评分系统
        score = 0
        reasons = []
        direction = None
        
        # 趋势判断
        if ma20 > ma50:
            score += 20
            reasons.append("MA20>MA50上涨趋势")
            direction = "LONG"
        else:
            score += 20
            reasons.append("MA20<MA50下跌趋势")
            direction = "SHORT"
        
        # RSI
        if direction == "LONG" and rsi < 30:
            score += 25
            reasons.append(f"RSI超卖({rsi:.1f})")
        elif direction == "SHORT" and rsi > 70:
            score += 25
            reasons.append(f"RSI超买({rsi:.1f})")
        elif 40 <= rsi <= 60:
            score += 10
        else:
            score += 5
        
        # MACD
        if macd["histogram"] > 0 and direction == "LONG":
            score += 20
            reasons.append("MACD金叉")
        elif macd["histogram"] < 0 and direction == "SHORT":
            score += 20
            reasons.append("MACD死叉")
        
        # K线形态
        if pattern:
            if pattern in ["BULLISH_ENGULFING", "HAMMER"] and direction == "LONG":
                score += 25
                reasons.append(f"形态:{pattern}")
            elif pattern in ["BEARISH_ENGULFING", "INVERTED_HAMMER"] and direction == "SHORT":
                score += 25
                reasons.append(f"形态:{pattern}")
        
        # 分数不够
        if score < self.min_score:
            logger.info(f"{symbol} 信号分数不足: {score}")
            return None
        
        # 计算入场、止损、止盈
        if direction == "LONG":
            entry = current_price
            stop_loss = max(sr["support"], entry * 0.97)  # 3%止损
            take_profit = entry + (entry - stop_loss) * 2  # 1:2盈亏比
        else:
            entry = current_price
            stop_loss = min(sr["resistance"], entry * 1.03)
            take_profit = entry - (stop_loss - entry) * 2
        
        return Signal(
            symbol=symbol,
            direction=direction,
            score=score,
            entry=entry,
            stop_loss=stop_loss,
            take_profit=take_profit,
            reason=" | ".join(reasons)
        )


if __name__ == "__main__":
    # 测试
    system = SignalSystem()
    print("信号系统初始化完成")
