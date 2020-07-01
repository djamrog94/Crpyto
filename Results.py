from prettytable import PrettyTable
import pandas as pd


class Results:
    def __init__(self, strat):
        self.executed_strat = strat
        self.df = pd.DataFrame(strat.positions)
        self.closing_balance = None
        self.win_trade = 0
        self.loss_trade = 0
        self.trades = 0
        self.nominal_returns = []
        self.percent_returns = []
        self.calc_returns()

    def num_completed_trades(self):
        return self.trades

    def amount_open(self):
        return self.executed_strat.position

    def num_win_trades(self):
        return self.win_trade

    def num_loss_trade(self):
        return self.loss_trade

    def get_nominal_returns(self):
        return sum(self.nominal_returns)

    def get_percent_returns(self):
        return sum(self.percent_returns) * 100

    def get_portfolio_percent_return(self):
        return (self.get_nominal_returns() / self.executed_strat.balance) * 100

    def calc_returns(self):
        self.closing_balance = self.executed_strat.balance
        avg_price = 0
        size = 0
        for i in range(len(self.df)):
            if self.df.iloc[i]['trade_type'] == 'OPEN':
                size = self.df.iloc[i]['amount']
                avg_price = self.df.iloc[i]['price']
            else:
                if self.df.iloc[i]['amount'] > 0:
                    # buying
                    if self.df.iloc[i]['price'] > avg_price:
                        avg_price += self.df.iloc[i]['amount'] / (size + self.df.iloc[i]['amount']) * avg_price
                    else:
                        avg_price -= self.df.iloc[i]['amount'] / (size + self.df.iloc[i]['amount']) * avg_price
                else:
                    # selling
                    profit = self.df.iloc[i]['amount'] * (avg_price - self.df.iloc[i]['price'])
                    if profit > 0:
                        self.win_trade += 1
                    else:
                        self.loss_trade += 1
                    self.nominal_returns.append(profit)
                    self.percent_returns.append(self.df.iloc[i]['price'] / avg_price - 1)

                size += self.df.iloc[i]['amount']
                if size == 0:
                    self.trades += 1
        self.closing_balance += self.get_nominal_returns()

    def display(self):
        output = PrettyTable(["Metric", "Value"])
        output.align['Metric'] = 'l'
        output.align['Value'] = 'l'
        output.add_row(['Number of Completed Trades', self.num_completed_trades()])
        output.add_row(['Value of Open Trades', f"${self.amount_open():.2f}"])
        output.add_row(['Starting Balance', f"${self.executed_strat.get_balance():.2f}"])
        output.add_row(['Ending Balance', f"${self.closing_balance:.2f}"])
        output.add_row(['$ P&L Change', f"${self.get_nominal_returns():.2f}"])
        output.add_row(['% P&L Change', f"{self.get_portfolio_percent_return():.3f}%"])
        output.add_row(['Number of Trades Won', self.num_win_trades()])
        output.add_row(['Number of Trades Lost', self.num_loss_trade()])

        return output

