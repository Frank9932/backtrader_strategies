import argparse
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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run backtesting with dynamic start and end parameters.')
    parser.add_argument('-s','--start', type=int, help='Start point of the parameter range.')
    parser.add_argument('-e','--end', type=int, help='End point of the parameter range.')
    
    args = parser.parse_args()
    start = args.start
    end = args.end

    cerebro = bt.Cerebro()
    cerebro.broker.setcash(100000)
    cerebro.broker.setcommission(commission=0.001)
 
    vt_buy_pct_range = [round(x * 0.1,1) for x in range(start, end + 1)]
    vt_sell_pct_range = [round(x * 0.1,1) for x in range(start, end + 1)]

    cerebro.optstrategy(
    _Strategy,
    vt_buy_pct=vt_buy_pct_range,
    vt_sell_pct=vt_sell_pct_range
    )

    data_feed = PandasData_Custom(dataname=df)
    cerebro.adddata(data_feed)

    results = cerebro.run()
