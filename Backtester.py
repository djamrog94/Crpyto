from Data_Gatherer import DataGatherer
import pandas as pd
import os


FEES = 0.002
SLIPPAGE = 0.002


class Backtester:
    def __init__(self, start, end, pair, strategy):
        self.pair = pair.upper()
        self.dg = DataGatherer(self.pair)
        self.start = self.dg.convert_string_to_timestamp(start)
        self.end = self.dg.convert_string_to_timestamp(end)
        self.strategy = strategy
        self.fess = FEES
        self.slip = SLIPPAGE

    def get_data(self):
        self.dg.connect_to_db()
        cmd = f"SELECT * FROM public.{self.pair} WHERE time >= '{self.start}' AND time <= '{self.end}'"
        self.dg.cur.execute(cmd)
        data = self.dg.cur.fetchall()
        df = pd.DataFrame(data, columns=self.dg.columns)
        print(df.head())

    def get_strat(self):
        if os.path.isfile(f'.strategies/{self.strategy}.py'):
            return True
        return False

    def back_test(self):
        import strategies.BasicStrat as bs
        from Strategy import Strategy
        Strategy.update()



def main():
    bb = Backtester("2020-06-02", "2020-06-04", "ethusd", 'BasicStrat')
    try:
        bb.get_data()
    except:
        print("Cannot get historical data for that time period!")
    if not bb.get_strat():
        print("That strategy doesn't exist!")
    bb.back_test()


if __name__ == '__main__':
    main()
