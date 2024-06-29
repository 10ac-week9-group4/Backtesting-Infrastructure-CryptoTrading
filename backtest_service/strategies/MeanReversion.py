import backtrader as bt

class MeanReversionStrategy(bt.Strategy):
    params = (
        ('bb_period', 20),
        ('bb_devfactor', 2),
        ('rsi_period', 14),
        ('oversold', 30),
        ('overbought', 70),
    )

    def __init__(self):
        self.bbands = bt.indicators.BollingerBands(period=self.params.bb_period, devfactor=self.params.bb_devfactor)
        self.rsi = bt.indicators.RSI(period=self.params.rsi_period)

    def next(self):
        if not self.position:
            if (self.data.close < self.bbands.bot and  # Oversold (below lower Bollinger Band)
                    self.rsi < self.params.oversold):  # RSI confirms oversold
                self.buy()
        else:
            if (self.data.close > self.bbands.mid or  # Reverts to mean (above middle band)
                    self.rsi > self.params.overbought):  # RSI confirms overbought
                self.sell()
