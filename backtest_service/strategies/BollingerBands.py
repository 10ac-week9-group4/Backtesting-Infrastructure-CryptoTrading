import backtrader as bt

class BollingerBandsStrategy(bt.Strategy):
    params = (
        ('period', 20),
        ('devfactor', 2)
    )

    def __init__(self):
        self.boll = bt.indicators.BollingerBands(self.data, period=self.p.period, devfactor=self.p.devfactor)

    def next(self):
        if self.position:  # In the market
            if self.data.close > self.boll.top:  # Overbought, exit long position
                self.close()
        else:  # Not in the market
            if self.data.close < self.boll.bot:  # Oversold, enter long position
                self.buy()
