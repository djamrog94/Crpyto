import krakenex
from sqlalchemy import create_engine
import psycopg2
import psycopg2.extras
from datetime import datetime
from datetime import timedelta
from datetime import timezone
import pytz
import time
import pandas as pd

UTC_TZ = pytz.timezone('UTC')
EST_TZ = pytz.timezone('America/New_York')


class DataGatherer:
    def __init__(self, pair):
        self.k = krakenex.API()
        self.k.load_key('key.txt')
        self.pair = pair.upper()
        self.conn = None
        self.cur = None
        self.start, self.end = 0, 0
        self.data = []
        self.engine = ''
        self.columns = ['price', 'volume', 'time', 'BS', 'ML', 'misc']

        with open('db_cred.txt', 'r') as f:
            creds = f.readlines()
        self.db_name = creds[0].rstrip()
        self.username = creds[1].rstrip()
        self.password = creds[2].rstrip()

    def convert_string_to_timestamp(self, date_string):
        dt = datetime.strptime(date_string, '%Y-%m-%d')
        return dt.replace(tzinfo=timezone.utc).timestamp()

    def convert_timestamp_to_date(self, date):
        return datetime.utcfromtimestamp(date)

    def convert_string_to_date(self, date):
        format = '%Y-%m-%d'
        return datetime.strptime(date, format)

    def create_db_engine(self):
        port = '5432'
        return create_engine(f'postgresql+psycopg2://{self.username}:{self.password}@localhost:{port}/{self.db_name}')

    def connect_to_db(self):
        self.conn = psycopg2.connect(f'dbname={self.db_name} user={self.username} password={self.password}')
        self.cur = self.conn.cursor()

    def collect_data(self, start, end):
        """
        this function collects data, either from scratch or updates
        saves to postgresql
        EVERYTHING GOING IN MUST BE UTC!!! kraken returns all dates in utc TZ
        :param start str YYYY-MM-DD
        :param end str YYYY-MM-DD
        :return: N/A
        """
        print(f"Gathering data for {self.pair} for the time period of {start} - {end}.")
        print("-----------------------------------------------------------------------\n")
        # convert string to utc timestamp, for api
        self.start = self.convert_string_to_timestamp(start)
        self.end = self.convert_string_to_timestamp(end)

        last_param = str(int(self.start * (10 ** 9)))
        last = self.start

        while last < self.end:
            params = {'pair': self.pair, 'since': last_param}
            resp = self.k.query_public('Trades', params)
            while len(resp) < 2:
                print("Timed out... Sleeping for 30 seconds.")
                time.sleep(30)
                resp = self.k.query_public('Trades', params)

            last_param = resp['result']['last']
            last = int(last_param) / (10 ** 9)
            self.data.extend(resp['result'][f'X{self.pair[:3]}Z{self.pair[3:]}'])
            print(f'{self.convert_timestamp_to_date(last)} | {datetime.now()}')
            time.sleep(1)

        # remove last row because next run will include this data
        for i in range(1, len(self.data)):
            if self.data[-i][2] < self.end:
                cut_off = i
                break
        self.data = self.data[:-cut_off + 1]

    def create_table(self):
        command = f'CREATE TABLE {self.pair} (price REAL, volume REAL, time VARCHAR(255),' \
                  f' BS VARCHAR(1), ML VARCHAR(1), misc VARCHAR(255))'
        self.connect_to_db()
        self.cur.execute(command)
        self.cur.close()
        self.conn.commit()
        self.conn.close()

    def insert_data_to_db(self):
        self.engine = self.create_db_engine()
        self.connect_to_db()
        df = pd.DataFrame(self.data)

        if len(df) > 0:
            # create (col1,col2,...)
            columns = ",".join(self.columns)

            # create VALUES('%s', '%s",...) one '%s' per column
            values = "VALUES({})".format(",".join(["%s" for _ in self.columns]))

            # create INSERT INTO table (columns) VALUES('%s',...)
            insert_stmt = f"INSERT INTO {self.pair} ({columns}) {values}"

            psycopg2.extras.execute_batch(self.cur, insert_stmt, df.values)
            self.conn.commit()
            self.cur.close()
            self.conn.close()
            # reset data for next collection
            self.data = []

    def convert_tick_data(self, time_frame):
        """

        :param time_frame: enter just number. i.e for 15 min, just enter "15".
        :return:
        """
        self.connect_to_db()
        self.cur.execute(f'SELECT * FROM public.{self.pair.lower()}')
        data = self.cur.fetchall()
        df = pd.DataFrame(data, columns=self.columns)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df = df.set_index('time')
        ohlc = df['price'].resample(f'{time_frame}Min').ohlc().bfill()
        vol = df['volume'].resample(f'{time_frame}Min').sum()
        # fix issue with wrong open price
        for i in range(1, len(ohlc)):
            new_open = ohlc.iloc[i - 1]['close']
            ohlc.iloc[i]['high'] = max(new_open, ohlc.iloc[i]['high'])
            ohlc.iloc[i]['low'] = min(new_open, ohlc.iloc[i]['low'])
            ohlc.iloc[i]['open'] = new_open

        self.cur.close()
        self.conn.commit()
        self.conn.close()
        return ohlc, list(vol)


def convert_timestamp_to_date(timestamp):
    temp = datetime.fromtimestamp(timestamp)
    return temp.replace(hour=0, minute=0, second=0, microsecond=0)


def convert_string_to_date(str_date):
    d = datetime.strptime(str_date, "%Y-%m-%d")
    return d.astimezone(UTC_TZ)


def convert_date_to_string(date):
    return datetime.strftime(date, "%Y-%m-%d")


def find_time(pair, start, end):
    """

    :param start: str; YYYY-MM-DD
    :param end: str; YYYY-MM-DD
    :return: list of times that need to be gathered of type (str; YYYY-MM-DD)
    """
    times = []
    dg = DataGatherer(pair)
    dg.connect_to_db()

    start = convert_string_to_date(start)
    end = convert_string_to_date(end)

    # comes in as timestamp
    dg.cur.execute(f'SELECT * FROM public.{pair.lower()} ORDER BY "time" ASC LIMIT 1')
    start_db = float(dg.cur.fetchone()[2])
    dg.cur.execute(f'SELECT * FROM public.{pair.lower()} ORDER BY "time" DESC LIMIT 1')
    end_db = float(dg.cur.fetchone()[2])

    start_db = convert_timestamp_to_date(start_db)
    end_db = convert_timestamp_to_date(end_db)
    # continue on i.e if start date is past last end date in sql

    # combo i.e need data before start date in sql and need data after end date in sql
    if start < start_db and end > end_db:
        times = [[start, start_db], [end_db + timedelta(days=1), end]]
        dg.cur.close()
        dg.conn.close()
        return [convert_date_to_string(t) for t in times[0]], \
               [convert_date_to_string(t) for t in times[1]]

    if start > end_db:
        times = [start, end]
    else:
        # if continuing from end point in db, must add one day to not overlap
        if end > end_db:
            times = [end_db + timedelta(days=1), end]

    # catch up i.e start date is before start date in sql
    if start < start_db:
        if end < start_db:
            print(f"Will add extra days, to avoid gap. You selected {end} for an end date,"
                  f"new end date will be {convert_timestamp_to_date(start_db)} to prevent gap.")
            times = [start, start_db]
        else:
            times = [start, end]

    # fill in gap cant allow cuz v hard!

    dg.cur.close()
    dg.conn.close()

    # times can't be the same!!!
    if times[0] == times[1]:
        raise ValueError(f'Start: {times[0]} End: {times[1]}\nNeed at least one day between start and end date!')

    times = [[convert_date_to_string(t) for t in times]]
    return times


def main():
    pair = input('Pair? ')
    dg = DataGatherer(pair)
    first_time = False
    try:
        dg.create_table()
        first_time = True
    except:
        pass
    start, end = input("Enter start and end date in format YYYY-MM-DD separated by a space: ").split(' ')
    if not first_time:
        times = find_time(pair, start, end)
        # only need to run one data collection
        if len(times) < 2:
            start_time, end_time = times[0][0], times[0][1]
            dg.collect_data(start_time, end_time)
            dg.insert_data_to_db()
        # need to run two data collection
        else:
            for tt in times:
                start_time, end_time = tt[0], tt[1]
                dg.collect_data(start_time, end_time)
                dg.insert_data_to_db()

                print(f'Successfully saved data for {start_time} to {end_time}!')
    # data collection for first time
    else:
        dg.collect_data(start, end)
        dg.insert_data_to_db()


if __name__ == '__main__':
    main()
