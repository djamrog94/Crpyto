import unittest
from Data_Gatherer import DataGatherer
import pandas as pd


class Data_Gatherer_Test(unittest.TestCase):
    def test_data_collection(self):
        self.dg = DataGatherer('ETHUSD')

        # first time data collect
        self.dg.collect_data('2019-01-03', '2019-01-04')

        # earlier start date only
        self.dg.collect_data('2019-01-02', '2019-01-04')

        # later start date only
        self.dg.collect_data('2019-01-02', '2019-01-05')

        # both dates updated
        self.dg.collect_data('2019-01-01', '2019-01-06')

        # gap fix
        self.dg.collect_data('2019-01-07', '2019-01-08')

        # all
        self.dg.collect_data('2019-01-01', '2019-01-10')

        df = pd.DataFrame(self.dg.data)
        test = pd.read_csv('test.csv')
        pd.testing.assert_frame_equal(df, test)


if __name__ == '__main__':
    unittest.main()
