import pandas as pd
import backtrader as bt 

def prepare_df(df):
    df['date'] = pd.to_datetime(df['date'])

    df['candle_fluctuation'] = df['high'] - df['close']
    # daily_fluctuation = df.set_index('timestamp').groupby(pd.Grouper(freq='D'))['candle_fluctuation'].max()
    df['daily_fluctuation'] = df.groupby(df['date'].dt.date)['candle_fluctuation'].transform('max')
    df['previous_daily_fluctuation'] = df['daily_fluctuation'].shift(24)

    df.dropna(subset=['previous_daily_fluctuation'], 
            inplace=True)
    return df

class VolatilityStrategyV0(bt.Strategy):
    params = (
       ('vt_buy_pct', 0.8),
       ('vt_sell_pct', 0.9), 

       )
    # 0.8 0.9  128251 
    # 0.3 0.9  129545
    def __init__(self):
        self.open = self.data.open
        self.close = self.data.close
        self.high = self.data.high
        self.low = self.data.low
        self.pdf =self.data.previous_daily_fluctuation 

    def next(self):
        if len(self) ==1:
            return
          
        buy_condition = self.close[0] > (self.close[-1] + self.pdf * self.params.vt_buy_pct)
        sell_condition= self.close[0] < (self.close[-1] - self.pdf * self.params.vt_sell_pct)

        
        if not self.position:
            if buy_condition:
                self.buy()
        else:
            if sell_condition:
                self.sell()
        
    # def log(self,txt):
    #     dt = self.datas[0].datetime.date(0)
    #     print("{}-------- {}".format(dt.isoformat(), txt))
    def stop(self):
        print(f"{self.params.vt_buy_pct}\n{self.params.vt_sell_pct}\n    {self.broker.getvalue()}")

class VolatilityStrategyV1(bt.Strategy):
    params = (
        ('vt_buy_pct', 0.3),
        ('vt_sell_pct', 0.9),
        ('vt_stoploss_pct', 0.5),  # 50% of volatility as stop loss
    )
    
    def __init__(self):
        self.open = self.data.open
        self.close = self.data.close
        self.high = self.data.high
        self.low = self.data.low
        self.order = None
        self.buy_price = None
        self.stop_loss = None

    def next(self):
        if len(self) == 1:
            return
        
        # Calculate the volatility as the difference between the previous day's high and close
        volatility = self.high[-1] - self.close[-1]

        # Define buy and sell conditions based on the current close price
        buy_condition = self.close[0] > (self.close[-1] + volatility * self.params.vt_buy_pct)
        sell_condition = self.close[0] < (self.close[-1] - volatility * self.params.vt_sell_pct)
        
        # Check if there is no position
        if not self.position:
            if buy_condition:
                # If buy condition met, buy and set the buy price and stop loss
                self.buy_price = self.close[0]
                self.stop_loss = self.buy_price - (volatility * self.params.vt_stoploss_pct)  # pct of volatility as stop loss
                self.order = self.buy()
        else:
            # If a position exists, check for stop loss condition or sell condition
            if self.close[0] < self.stop_loss:
                self.order = self.sell(comment="Stop Loss")
            elif sell_condition:
                self.order = self.sell(comment="Sell Condition")

    def stop(self):
        # Output the final value of the portfolio
        print(f"{self.params.vt_buy_pct}\n{self.params.vt_sell_pct}\n                 {self.broker.getvalue()}")