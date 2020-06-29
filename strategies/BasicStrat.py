from strategies.Strategy import Strategy


class BasicStrat(Strategy):
    def __init__(self, balance):
        super().__init__(balance)

    def test(self):
        print("hi")