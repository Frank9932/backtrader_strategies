import backtrader as bt
import os
from pathlib import Path
import datetime





# class bk(bt.Strategy):
#     params = (
#         ('maOBVperiod', 10),
#     )
#     def __init__(self):
    
#     def stop(self):
#         print(self.params.maOBVperiod, self.broker.getvalue())


   
class MACDStrategy(bt.Strategy):
    params = (
        ('macd1', 10),
        ('macd2', 21),
        ('macdsignal', 5),
        ('maperiod', 41),
        ('stop_loss_percent', 1),  
        ('take_profit_percent', 2),
    )

    def __init__(self):
        self.kelly_fraction = 0.0  # initialize Kelly fraction to 0

        self.dataclose = self.datas[0].close
        self.sma = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.params.maperiod)

        self.macd = bt.indicators.MACD(self.data.close,
                                       period_me1=self.params.macd1,
                                       period_me2=self.params.macd2,
                                       period_signal=self.params.macdsignal)
        self.crossover = bt.indicators.CrossOver(self.macd.macd, self.macd.signal)

    def next(self):
        if not self.position:  # not in the market
            self.kelly_fraction = (self.pnl / self.size) / self.broker.getvalue()
            if self.crossover > 0:  # if fast crosses slow to the upside
                self.buy()  # enter long

        # elif self.crossover < 0:  # in the market & fast crosses slow to the downside
        #     self.close()  # close long position
          
        else:
            profit_percent = (self.dataclose[0] - self.position.price) / self.position.price * 100.0
            if profit_percent > self.params.take_profit_percent:  # 如果达到止盈条件
                # self.log('TAKE PROFIT, SELLING')
                # self.order = self.sell()
                self.close()
            elif profit_percent < -self.params.stop_loss_percent:  # 如果达到止损条件
                # self.log('STOP LOSS, SELLING')
                # self.order = self.sell()
                self.close()

    def stop(self):
        # 策略结束时调用
        print(self.params.macd1,self.params.macd2,self.params.macdsignal,self.broker.getvalue())
        # 10 21 5 100009290.26154998

if __name__ == '__main__':
    data_path = Path(os.getcwd()) / 'data/BTC-USD.csv'
    cerebro = bt.Cerebro()
    cerebro.broker.setcash(100000000)
    # cerebro.broker.setcommission(commission=0.001)
    # cerebro.addstrategy(MACDStrategy)
    # To optimize strategy, uncomment the following line and comment out the addstrategy line above
    # cerebro.optstrategy(MACDStrategy, macd1=range(10, 15), macd2=range(20, 30), macdsignal=range(5, 10), maperiod=range(7, 50), take_profit_percent=range(2, 10),)
    cerebro.optstrategy(OBVStrategy, maOBVperiod=range(7, 50),)
    
    # Add a data feed
    data = bt.feeds.YahooFinanceCSVData(
        dataname=str(data_path),
        fromdate=datetime.datetime(2022, 12, 9),
        todate=datetime.datetime(2024, 2, 9),
    )
    cerebro.adddata(data)
    cerebro.run()
    # cerebro.plot()


# class TestStrategy(bt.Strategy):
#     params = (
#         ('maperiod', 41),
#         ('stop_loss_percent', 1),  # 止损百分比
#         ('take_profit_percent', 2),  # 止盈百分比
#     )

#     def __init__(self):
#         # 定义指标和变量
#         self.dataclose = self.datas[0].close
#         self.order = None
#         # 使用Simple Moving Average作为指标
#         self.sma = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.params.maperiod)

#     def notify_order(self, order):
#         # 订单通知处理
#         if order.status in [order.Completed]:
#             # print()
#             if order.isbuy():
#                 self.log("Buy Executed {}".format(order.executed.price))
#             elif order.issell():
#                 self.log("Sell Executed {}".format(order.executed.price))
#                 self.buyprice = None
#         elif order.status in [order.Canceled, order.Margin, order.Rejected]:
#             self.log("Order Canceled/Margin/Rejected")
#         self.bar_executed = len(self)
#         self.order = None  # 重置self.ord   er为None，允许创建新的订单

#     def next(self):
#         # 检查是否有未完成的订单
#         if self.order:
#             return

#         # 执行买卖逻辑
#         if not self.position:  # 如果未持仓
#             if self.dataclose[0] > self.sma[0]:  # 如果收盘价高于SMA
#                 self.order = self.buy()  # 买入
#         else:  # 如果已持仓
#             profit_percent = (self.dataclose[0] - self.position.price) / self.position.price * 100.0
#             if profit_percent > self.params.take_profit_percent:  # 如果达到止盈条件
#                 self.log('TAKE PROFIT, SELLING')
#                 self.order = self.sell()
#             elif profit_percent < -self.params.stop_loss_percent:  # 如果达到止损条件
#                 self.log('STOP LOSS, SELLING')
#                 self.order = self.sell()

#     def log(self,txt):
#         dt = self.datas[0].datetime.date(0)
#         # print("{} -- {}".format(dt.isoformat(), txt))

#     def stop(self):
#         # 策略结束时调用
#         print(self.params.maperiod, self.broker.getvalue())

# if __name__ == '__main__':
#     # 设置数据路径
#     data_path = Path(os.getcwd()) / 'data/BTC-USD.csv'
#     cerebro = bt.Cerebro()
#     cerebro.broker.setcash(100000000)
#     cerebro.broker.setcommission(commission=0.001)

#     cerebro.addstrategy(TestStrategy)  # 添加策略
#     # cerebro.optstrategy(TestStrategy,maperiod=range(7, 56))
#     data = bt.feeds.YahooFinanceCSVData(
#         dataname=str(data_path),
#         fromdate=datetime.datetime(2022, 12, 9),
#         todate=datetime.datetime(2024, 2, 9),
#     )
#     cerebro.adddata(data)  # 添加数据
#     cerebro.run()  # 运行策略
#     cerebro.addobserver(bt.observers.BuySell, barplot=True, bardist=0.0025)  # 添加观察者
#     cerebro.plot()  # 绘图
