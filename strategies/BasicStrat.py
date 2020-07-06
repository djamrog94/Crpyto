from strategies.Strategy import Strategy


class myStrategy(Strategy):
    def __init__(self, balance):
        super().__init__(balance)

    def should_buy(self):
        if self.index % 10_000 == 0:
            return True

    def update(self):
        if self.index % 15_000 == 0:
            return True

    def go_long(self):
        dollar_amount = self.balance / 100
        share_amount = self.dollar_to_share(dollar_amount)
        self.make_trade("OPEN", "LONG", "MARKET", share_amount)
        self.position += share_amount




