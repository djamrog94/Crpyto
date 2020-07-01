from Data_Gatherer import DataGatherer
from Results import Results
import pandas as pd
import os
import importlib


FEES = 0.002
SLIPPAGE = 0.002
BALANCE = 10_000


class Backtester:
    def __init__(self, start, end, pair, strategy):
        self.pair = pair.upper()
        self.dg = DataGatherer(self.pair)
        self.start = self.dg.convert_string_to_timestamp(start)
        self.end = self.dg.convert_string_to_timestamp(end)
        self.strategy = strategy
        self.fess = FEES
        self.slip = SLIPPAGE
        self.data = pd.DataFrame()

    def get_data(self):
        self.dg.connect_to_db()
        cmd = f"SELECT * FROM public.{self.pair} WHERE time >= '{self.start}' AND time <= '{self.end}'"
        self.dg.cur.execute(cmd)
        data = self.dg.cur.fetchall()
        self.data = pd.DataFrame(data, columns=self.dg.columns)

    def get_strat(self):
        if os.path.isfile(f'strategies/{self.strategy}.py'):
            return True
        return False

    def back_test(self):
        strat_impl = importlib.import_module(f'strategies.{self.strategy}')
        strat = strat_impl.BasicStrat(BALANCE)
        for idx, r in enumerate(range(len(self.data))):
            strat.each_time(self.data.iloc[r], idx)
            print(f"{idx} / {len(self.data)} completed!")
        return strat

    def results(self):
        pass


def main():
    bb = Backtester("2020-06-02", "2020-06-04", "ethusd", 'BasicStrat')
    try:
        bb.get_data()
    except:
        print("Cannot get historical data for that time period!")
    if not bb.get_strat():
        print("That strategy doesn't exist!")
    executed_strat = bb.back_test()
    rr = Results(executed_strat)
    print(f"{'*' * 15} Results for: {'*' * 15}")
    print(f"{'*' * 15} {bb.strategy}! {'*' * 15}")
    print(rr.display())


if __name__ == '__main__':
    main()
