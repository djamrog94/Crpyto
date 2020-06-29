class Strategy:
    def __init__(self, balance):
        self.positions = []
        self.history = []
        self.balance = balance

    def should_buy(self):
        pass

    def should_sell(self):
        pass

    def update(self):
        pass


