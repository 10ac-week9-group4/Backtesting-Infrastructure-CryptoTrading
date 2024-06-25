from backtrader import bt

# Define the strategy
class SmaCrossOver(bt.Strategy):
    params = (('pfast', 50), ('pslow', 200),)  # Fast and slow MA periods

    def __init__(self):
        sma_fast = bt.ind.SMA(self.data, period=self.params.pfast)
        sma_slow = bt.ind.SMA(self.data, period=self.params.pslow)
        self.crossover = bt.ind.CrossOver(sma_fast, sma_slow)

    def next(self):
        if not self.position:  # Not in the market
            if self.crossover > 0:  # Fast MA crosses above slow MA
                self.buy()  # Enter long position
        elif self.crossover < 0:  # Fast MA crosses below slow MA
            self.close()  # Exit long position
