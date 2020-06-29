class Strategy:
    def __init__(self, balance):
        self.positions = []
        self.pending = []
        self.history = []
        self.balance = balance
        self.data = []
        self.index = 0

    def should_buy(self):
        pass

    def should_sell(self):
        pass

    def update(self):
        pass

    def create_record(self, side, type, amount, price, time):
        return {'side': side,
                'type': type,
                'amount': amount,
                'price': price,
                'time_opened': time,
                'pos_closed': []
                }

    def go_long(self, amount):
        self.positions.append(self.create_record("LONG", "MARKET", amount, self.data[0], self.data[2]))
        self.history.append(self.create_record("LONG", "MARKET", amount, self.data[0], self.data[2]))

    def go_short(self, amount):
        self.positions.pop()
        self.history.append(self.create_record("SHORT", "MARKET", amount, self.data[0], self.data[2]))


