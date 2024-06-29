import backtrader as bt

class RSID_SMA(bt.Strategy):

    def __init__(self):
        self.rsi = bt.indicators.RSI_SMA(self.data, period=14)

    def next(self):
        if not self.position:
            if self.data.close[0] < self.data.close[-1] and self.rsi[0] > self.rsi[-1]:  # Bullish divergence
                self.buy()
        else:
            if self.data.close[0] > self.data.close[-1] and self.rsi[0] < self.rsi[-1]:  # Bearish divergence
                self.close()
