import backtrader as bt

class MovingAverageCrossoverStrategy(bt.Strategy):
    params = (
        ('short_period', 30),
        ('long_period', 60),
    )

    def log(self, txt, dt=None):
        ''' Logging function for the strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the close price in the data[0] dataseries
        self.dataclose = self.datas[0].close

        # Create moving averages
        self.short_ma = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.params.short_period)
        self.long_ma = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.params.long_period)

    def next(self):
        if self.position.size == 0:  # Not in the market
            if self.short_ma[0] > self.long_ma[0] and self.short_ma[-1] <= self.long_ma[-1]:
                self.buy()
                self.log('BUY CREATE, %.2f' % self.dataclose[0])

        elif self.position.size > 0:  # In the market with a long position
            if self.short_ma[0] < self.long_ma[0] and self.short_ma[-1] >= self.long_ma[-1]:
                self.sell()
                self.log('SELL CREATE, %.2f' % self.dataclose[0])


