import backtrader as bt 
import os
from pathlib import Path
import pandas as pd

from strategies import prepare_df
from strategies import VolatilityStrategyV0 as _Strategy

feather_file_path = Path(os.getcwd())/'data'/'BTC_USDT-1h.feather'

df = pd.read_feather(feather_file_path)
df = prepare_df(df)
df.set_index('date', inplace=True)

class PandasData_Custom(bt.feeds.PandasData):
    lines = ('previous_daily_fluctuation',)
    params = (
        ('previous_daily_fluctuation', -1),
        # ('fromdate' ,datetime(2019, 1, 1)),
        # ('todate', datetime(2019, 2, 1)),
    )


if True :
    cerebro = bt.Cerebro()
    cerebro.broker.setcash(100000)
    cerebro.broker.setcommission(commission=0.001)

    cerebro.addstrategy(_Strategy)

    data_feed = PandasData_Custom(dataname=df)
    cerebro.adddata(data_feed)


    
    results = cerebro.run()


cerebro.plot()