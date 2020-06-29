from Data_Gatherer import DataGatherer
import pandas as pd


class Backtester:
    def __init__(self, start, end, pair, strategy):
        self.pair = pair.upper()
        self.dg = DataGatherer(self.pair)
        self.start = self.dg.convert_string_to_timestamp(start)
        self.end = self.dg.convert_string_to_timestamp(end)
        self.strategy = strategy

    def get_data(self):
        self.dg.connect_to_db()
        cmd = f"SELECT * FROM public.{self.pair} WHERE time >= '{self.start}' AND time <= '{self.end}'"
        self.dg.cur.execute(cmd)
        data = self.dg.cur.fetchall()
        df = pd.DataFrame(data, columns=self.dg.columns)


def main():
    bb = Backtester("2020-05-27", "2020-05-30", "ethusd", 'Basic_Strat')
    bb.get_data()


if __name__ == '__main__':
    main()

