from datamodel import Listing, OrderDepth, Trade, TradingState, Order
import numpy as np

#product is called Pearl and Banana, each with 20 position limit
# we use sma for pearls and ema for banana as the acceptable price
# we need to remember to update our position and make sure that the order does not exceed position limit

class Trader:
    def __init__(self):
        self.pos_lim = {'PEARLS': 20, 'BANANAS': 20}
        self.position = {'PEARLS': 0, 'BANANAS': 0}
        self.ema = {"PEARLS": 0, "BANANAS":0}
    #average price from market as pearl is stable
    def fairprice(self, state, product, duration): #this should be called recursively later, duration is how many data points we want to take average over
        alpha = 2/(1+duration)
        order_depth = state.order_depths[product] #get a list of bid and ask prices
        best_ask = min(order_depth.sell_orders.keys()) if len(order_depth.sell_orders) != 0 else None
        best_bid = max(order_depth.buy_orders.keys()) if len(order_depth.buy_orders) != 0 else None
        if best_ask and best_bid:
            mid_price = (best_ask + best_bid)/2
        if self.ema[product] == 0:
            self.ema[product] = mid_price
        else:
            if mid_price:
                self.ema[product] = self.ema[product] * alpha + (1 - alpha) * mid_price

        return self.ema[product]

    
    def updatestatus(self, state):
        if state.own_trades.keys():
            pos_var = 0
            for product, past_trades in state.own_trades.items():
                for trade in past_trades:
                    if trade.buyer == 'SUBMISSION':
                        pos_var += trade.quantity
                    if trade.seller == 'SUBMISSION':
                        pos_var -= trade.quantity
                self.position[product] += pos_var
        else:
            return
                            
    def run(self, state):
        results = {}
        #get the most updated order first
        self.updatestatus(state)
        
        for item in state.order_depths.keys(): #order depth is a subclass under state
            if item == 'BANANAS':
                orders = []
                banana_order = state.order_depths[item]
                #find the average of pearl based on market order
                acceptable_price = self.fairprice(state, 'BANANAS', 3)
                best_ask_price = min(banana_order.sell_orders.keys())
                best_bid_price = max(banana_order.buy_orders.keys())
                current_price = (best_ask_price + best_bid_price)/2
                #we are buying first                        
                if len(banana_order.sell_orders) != 0: #ask price is the price other market participants want to sell and we are buying in 
                    best_ask_volume = banana_order.sell_orders[best_ask_price] if best_ask_price is not None else None
                    print(best_ask_price)
                    print(acceptable_price)
                    if acceptable_price is not None and current_price > acceptable_price: 
                        if best_ask_volume is not None:
                            buyable_volume = min(2, self.pos_lim['BANANAS'] - self.position['BANANAS'])
                        else:
                            buyable_volume = self.pos_lim['BANANAS'] - self.position['BANANAS']
                        if buyable_volume > 0:
                            print("BUY", 'BANANAS', str(buyable_volume) + "x", best_ask_price)
                            orders.append(Order('BANANAS', best_ask_price, buyable_volume))
 
                       
                if len(banana_order.buy_orders) != 0:

                    best_bid_volume = banana_order.buy_orders[best_bid_price] if best_bid_price is not None else None
                    print(best_bid_price)
                    print(acceptable_price)
                    if acceptable_price is not None and current_price < acceptable_price: #other people want to buy and we are selling
                        if best_bid_volume is not None:
                            sellable_volume = max(-2, -self.pos_lim['BANANAS'] - self.position['BANANAS'])
                        else:
                            sellable_volume = -self.pos_lim['BANANAS'] - self.position['BANANAS']
            
                        if sellable_volume < 0:
                            print("SELL", 'BANANAS', str(sellable_volume) + "x", best_bid_price)
                            orders.append(Order('BANANAS', best_bid_price, sellable_volume))
                      
                results['BANANAS'] = orders

        return results
