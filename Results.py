from prettytable import PrettyTable


class Results:
    def __init__(self, strat):
        self.executed_strat = strat
        self.closing_balance = self.executed_strat.get_balance()
        self.win_trade = 0
        self.loss_trade = 0

    def num_completed_trades(self):
        return len(self.executed_strat.history)

    def num_open_trades(self):
        return len(self.executed_strat.positions)

    def num_win_trades(self):
        return self.win_trade

    def num_loss_trade(self):
        return self.loss_trade

    def calc_returns(self):
        returns = []
        for trade in self.executed_strat.history:
            open = trade['amount'] * trade['price']
            close = trade['pos_closed']['amount'] * trade['pos_closed']['price']
            dollar_return = close - open
            if dollar_return >= 0:
                self.win_trade += 1
            else:
                self.loss_trade -= 1
            percent_return = close / open - 1
            returns.append([dollar_return, percent_return])
        return returns

    def calc_pl(self):
        returns = self.calc_returns()
        for ret in returns:
            self.closing_balance += ret[0]

        return self.closing_balance, self.closing_balance / self.executed_strat.get_balance() - 1

    def display(self):
        output = PrettyTable(["Metric", "Value"])
        output.align['Metric'] = 'l'
        output.align['Value'] = 'l'
        output.add_row(['Number of Completed Trades', self.num_completed_trades()])
        output.add_row(['Number of Open Trades', self.num_open_trades()])
        output.add_row(['Starting Balance', f"${self.executed_strat.get_balance():.2f}"])
        close_dollar, close_percent = self.calc_pl()
        output.add_row(['$ P&L Change', f"${close_dollar:.2f}"])
        output.add_row(['% P&L Change', f"{close_percent:.3f}%"])
        output.add_row(['Number of Won Trades', self.num_win_trades()])
        output.add_row(['Number of Lost Trades', self.num_loss_trade()])

        return output

