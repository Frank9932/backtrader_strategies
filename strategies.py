import pandas as pd
import backtrader as bt 

def prepare_df(df):
    df['date'] = pd.to_datetime(df['date'])

    df['candle_fluctuation'] = df['high'] - df['close']
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
        
        self.order = None
        self.trade_count = 0
        self.win_count = 0
        self.loss_count = 0
        self.total_profit = 0.0

    def notify_trade(self, trade):
        if trade.isclosed:
            self.trade_count += 1
            self.total_profit += trade.pnl  # pnl is profit and loss for this trade
            if trade.pnl > 0:
                self.win_count += 1
            elif trade.pnl < 0:
                self.loss_count +=1

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
        if self.trade_count > 0:
            win_rate = (self.win_count / self.trade_count) * 100
            average_profit = self.total_profit / self.trade_count
        else:
            win_rate = 0.0
            average_profit = 0.0

        # 输出最终值
        print(f"Buy Threshold: {self.params.vt_buy_pct}\nSell Threshold: {self.params.vt_sell_pct}")
        print(f"Final Portfolio Value: {self.broker.getvalue()}")
        print(f"Total Trades: {self.trade_count}")
        print(f"Winning Trades: {self.win_count}")
        print(f"Win Rate: {win_rate:.2f}%")
        print(f"Total Profit: {self.total_profit:.2f}")
        print(f"Average Profit per Trade: {average_profit:.2f}")

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
        print(f"{self.params.vt_buy_pct}\n{self.params.vt_sell_pct}\n {self.broker.getvalue()}")