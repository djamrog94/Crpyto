from strategies.Strategy import Strategy


class BasicStrat(Strategy):
    def __init__(self, balance):
        super().__init__(balance)

    def should_buy(self):
        if self.index % 10_000 == 0:
            return True

    def update(self):
        if self.index % 15_000 == 0:
            return True

    def go_long(self):
        amount = self.balance / 100
        self.make_trade("OPEN", "LONG", "MARKET", amount)
        self.position += amount




