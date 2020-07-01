from strategies.Strategy import Strategy


class BasicStrat(Strategy):
    def __init__(self, balance):
        super().__init__(balance)

    def each_time(self, row, index):
        self.data = row
        self.index = index
        if len(self.positions) != 0:
            self.update()
        else:
            self.should_buy()

    def should_buy(self):
        if self.index % 10_000 == 0:
            self.go_long(self.balance / 1000)

    def should_sell(self):
        if self.index % 10_000 == 0:
            self.go_long(self.balance / 1000)

    def update(self):
        if self.index % 15_000 == 0:
            self.liquidate(0, self.data[2])

