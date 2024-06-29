import backtrader as bt

class MACDCrossoverStrategy(bt.Strategy):
    params = (
        ('fastperiod', 12),  
        ('slowperiod', 26),  
        ('signalperiod', 9)  
    )

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.order = None
        
        # Initialize MACD indicator
        self.macd = bt.indicators.MACD(
            self.data, 
            period_me1=self.params.fastperiod,
            period_me2=self.params.slowperiod,
            period_signal=self.params.signalperiod
        )

        # Additional indicators for visual analysis (optional)
        bt.indicators.MACDHisto(self.data) 

    def next(self):
        if self.order:  # Check for pending orders
            return

        if not self.position:  # Not in the market
            if self.macd.macd[0] > self.macd.signal[0] and self.macd.macd[-1] <= self.macd.signal[-1]:  # MACD crossover
                self.log(f'BUY CREATE, {self.dataclose[0]:.2f}')
                self.order = self.buy()
        else:
            if self.macd.macd[0] < self.macd.signal[0] and self.macd.macd[-1] >= self.macd.signal[-1]:  # MACD crossover
                self.log(f'SELL CREATE, {self.dataclose[0]:.2f}')
                self.order = self.sell()
