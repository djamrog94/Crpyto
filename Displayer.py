from Data_Gatherer import DataGatherer
import mplfinance as mpf


class Displayer:
    def __init__(self, pair, time):
        self.pair = pair.upper()
        self.dg = DataGatherer(self.pair)
        self.time = time

    def print_candles(self):
        df, vol = self.dg.convert_tick_data(self.time)
        df['Volume'] = vol
        df = df.rename(columns={'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close'})
        mpf.plot(df, type='line', volume=True)


def main():
    time = f"{60*3}"
    dd = Displayer("ethusd", time)
    dd.print_candles()


if __name__ == '__main__':
    main()
