class Strategy:
    def __init__(self, balance):
        self.position = 0
        self.positions = []
        self.balance = balance
        self.data = []
        self.index = 0

    def each_time(self, row, index):
        self.data = row
        self.index = index
        if self.position != 0:
            result = self.update()
            if result:
                self.liquidate()
        else:
            result = self.should_buy()
            if result:
                self.go_long()

    def get_balance(self):
        return self.balance

    def should_buy(self):
        pass

    def should_sell(self):
        pass

    def update(self):
        pass

    def go_long(self):
        pass

    def dollar_to_share(self, dollar_amount):
        return dollar_amount / self.data[0]

    def share_to_dollar(self, share_amount):
        return share_amount * self.data[0]

    def liquidate(self):
        amount = -self.position
        self.make_trade("LIQUIDATE", "SHORT", "MARKET", amount)
        self.position += amount

    def create_record(self, trade_type, side, type, amount, time, price):
        """

        :param trade_type:
        :param side:
        :param type:
        :param amount: this must be amount in shares!!
        :param time:
        :param price:
        :return:
        """
        return {'trade_type': trade_type,
                'side': side,
                'order_type': type,
                'amount': amount,
                'time': time,
                'price': price,
                }

    def make_trade(self, trade_type, side, order_type, amount):
        self.positions.append(self.create_record(trade_type,
                                                 side,
                                                 order_type,
                                                 amount,
                                                 self.data[2],
                                                 self.data[0],
                                                 ))





