from backtesting import Strategy

class MyStrat(Strategy):
    initsize = 0.3
    mysize = initsize
    def init(self):
        super().init()
    
    def next(self):
        super().next()
        
        if self.data.BuySell ==1:   
            self.buy()
        
        elif self.data.BuySell ==2:         
            self.sell()
            
