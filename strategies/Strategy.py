class Strategy:
    def __init__(self, balance, fees, slippage):
        self.positions = []
        self.pending = []
        self.history = []
        self.balance = balance
        self.fee_percent = fees
        self.slippage_percent = slippage
        self.data = []
        self.index = 0
        self.trade_num = 0

    def get_balance(self):
        return self.balance

    def should_buy(self):
        pass

    def should_sell(self):
        pass

    def update(self):
        pass

    def calc_fees(self, price):
        return price * self.fee_percent

    def calc_slippage(self, price):
        return price * self.slippage_percent

    def create_record(self, trade_num, side, type, amount, price, fees, slippage, time, closed):
        return {'index': trade_num,
                'side': side,
                'type': type,
                'amount': amount,
                'price': price,
                'fees': fees,
                'slippage': slippage,
                'time_opened': time,
                'pos_closed': [closed]
                }

    def go_long(self, amount):
        self.positions.append(self.create_record(self.trade_num,
                                                 "LONG",
                                                 "MARKET",
                                                 amount,
                                                 self.data[0],
                                                 self.calc_fees(amount * self.data[0]),
                                                 self.calc_slippage(amount * self.data[0]),
                                                 self.data[2],
                                                 None))

    def liquidate(self, trade_num, time):
        liquidate_trade = self.positions.pop(trade_num)
        amount = liquidate_trade['amount']
        side = liquidate_trade['side']
        if side == 'LONG':
            opp = "SHORT"
        else:
            opp = "LONG"
        liquidate_trade['pos_closed'] = self.create_record(trade_num,
                                                           opp,
                                                           "MARKET",
                                                           amount,
                                                           self.data[0],
                                                           self.calc_fees(amount * self.data[0]),
                                                           self.calc_slippage(amount * self.data[0]),
                                                           time,
                                                           None)
        self.history.append(liquidate_trade)



