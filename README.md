# 自动化交易系统

## 快速启动

```bash
cd ~/.hermes/workspace/auto_trading
python3 trading_engine.py
```

## 模块说明

| 文件 | 功能 | 状态 |
|------|------|------|
| binance_api.py | 币安Testnet API封装 | ✅ |
| signal_system.py | 技术指标+信号生成 | ✅ |
| risk_control.py | 风控系统 | ✅ |
| trading_engine.py | 交易引擎主程序 | ✅ |
| push_system.py | 推送通知 | ✅ |

## 信号系统功能

- MA/EMA均线计算
- RSI指标
- MACD指标
- K线形态识别（吞没、锤子）
- 支撑阻力位
- 信号评分（0-100分）

## 风控规则

- 单笔最大风险: 2%
- 最大总仓位: 50%
- 回撤警告: 10%
- 回撤停止: 20%
- 最小盈亏比: 1.5

## 验证标准

- 胜率 > 50%
- 盈亏比 > 1.5
- 最大回撤 < 20%
- 连续3个月盈利后转实盘
