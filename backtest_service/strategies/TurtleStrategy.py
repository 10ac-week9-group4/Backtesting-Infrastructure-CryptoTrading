import backtrader as bt

class TurtleStrategy(bt.Strategy):
    params = (
        ('long_period', 20),
        ('short_period', 10),
        ('atr_period', 20)
    )

    def __init__(self):
        self.long_entry = bt.indicators.Highest(self.data.high, period=self.p.long_period)
        self.short_entry = bt.indicators.Lowest(self.data.low, period=self.p.short_period)
        self.atr = bt.indicators.AverageTrueRange(self.data, period=self.p.atr_period)

    def next(self):
        if not self.position:  # Not in the market
            if self.data.close[0] > self.long_entry[0]:  # Breakout above long-term high
                self.buy(size=self.calculate_position_size())
        else:  # In the market
            if self.data.close[0] < self.short_entry[0]:  # Breakout below short-term low
                self.close()

    def calculate_position_size(self):
        risk = 0.01  # 1% risk per trade
        stop_loss = self.atr[0]  # Use ATR for stop-loss
        return (self.broker.getvalue() * risk) // stop_loss
