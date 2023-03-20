from datamodel import Listing, OrderDepth, Trade, TradingState, Order
import numpy as np

#product is called Pearl and Banana, each with 20 position limit
# we use sma for pearls and ema for banana as the acceptable price
# we need to remember to update our position and make sure that the order does not exceed position limit

class Trader:
    def __init__(self):
        self.pos_lim = {'PEARLS': 20, 'BANANAS': 20}
        self.position = {'PEARLS': 0, 'BANANAS': 0}
        self.ema = {"PEARLS": 0, "BANANAS":5000}
    #average price from market as pearl is stable
    def fairprice(self, state, product, duration): #this should be called recursively later, duration is how many data points we want to take average over
        alpha = 2/(1+duration)
        order_depth = state.order_depths[product] #get a list of bid and ask prices
        best_ask = min(order_depth.sell_orders.keys()) if len(order_depth.sell_orders) != 0 else None
        best_bid = max(order_depth.buy_orders.keys()) if len(order_depth.buy_orders) != 0 else None
        if best_ask and best_bid:
            mid_price = (best_ask + best_bid)/2
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
                acceptable_price = self.fairprice(state, 'BANANAS',7)
                #we are buying first                        
                if len(banana_order.sell_orders) > 0: #ask price is the price other market participants want to sell and we are buying in 
                    best_ask_price = min(banana_order.sell_orders.keys())
                    ask_volume = banana_order.sell_orders[best_ask_price]
                    if  acceptable_price and best_ask_price < acceptable_price:
                        if self.position['BANANAS'] < 20 -(-ask_volume):
                            print('BUY BANANAS'+',' + str(-ask_volume)+',' + str(best_ask_price))
                            orders.append(Order('BANANAS', best_ask_price, -ask_volume))
                        else:
                            print('BUY BANANAS'+',' + str(20 - self.position['BANANAS'])+',' + str(best_ask_price))
                            orders.append(Order('BANANAS', best_ask_price, 20 - self.position['BANANAS']))
 
                       
                if len(banana_order.buy_orders) > 0:
                    best_bid_price = min(banana_order.buy_orders.keys())
                    bid_volume = banana_order.buy_orders[best_bid_price] #bid/ask is about other market participants
                    if best_bid_price > acceptable_price: #other people want to buy and we are selling
                        if self.position['BANANAS'] > bid_volume:
                            print('SELL BANANAS'+',' +str(bid_volume)+',' + str(best_bid_price)) #we are effectively concatenant a string here, so we must convert integer to string first
                            orders.append(Order('BANANAS', best_bid_price, bid_volume))
                        else:
                            print('SELL BANANAS'+',' +str(self.position['BANANAS'])+',' + str(best_bid_price)) #we are effectively concatenant a string here, so we must convert integer to string first
                            orders.append(Order('BANANAS', best_bid_price, self.position['BANANAS']))

                results['BANANAS'] = orders
        return results