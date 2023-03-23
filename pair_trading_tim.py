import collections
from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order
import numpy as np


class Trader:
    def __init__(self):
        self.pos_limit = {"PEARLS": 20, "BANANAS": 20, "COCONUTS": 600, "PINA_COLADAS": 300}
        self.pos = {"PEARLS": 0, "BANANAS": 0, "COCONUTS": 0, "PINA_COLADAS": 0}
        self.sma = {"PEARLS": [], "BANANAS": []}
        self.last_timestamp = {"PEARLS": 0, "BANANAS": 0, "COCONUTS": 0, "PINA_COLADAS": 0}
        self.ratio = []
        # self.banana_acceptable_price = 0

    def get_order_book_info(self, order_depth):
        best_ask = min(order_depth.sell_orders.keys()) if len(order_depth.sell_orders) != 0 else None
        best_ask_volume = order_depth.sell_orders[best_ask] if best_ask is not None else None
        best_bid = max(order_depth.buy_orders.keys()) if len(order_depth.buy_orders) != 0 else None
        best_bid_volume = order_depth.buy_orders[best_bid] if best_bid is not None else None
        avg = (best_bid + best_ask) / 2 if best_bid is not None and best_ask is not None else None
        return best_ask, best_ask_volume, best_bid, best_bid_volume, avg

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        # Initialize the method output dict as an empty dict
        result = {}
        print("****************")

        # Update positions
        for product, trades in state.own_trades.items():
            if len(trades) == 0 or trades[0].timestamp == self.last_timestamp[product]:
                continue
            pos_delta = 0
            for trade in trades:
                # print(trade.buyer, trade.seller, trade.price, trade.quantity, trade.symbol)
                if trade.buyer == "SUBMISSION":
                    # We bought product
                    pos_delta += trade.quantity
                elif trade.seller == "SUBMISSION":
                    pos_delta -= trade.quantity
            self.pos[product] += pos_delta
            self.last_timestamp[product] = trades[0].timestamp
            print(product, self.pos[product])
        
        # Trading Pearls
        product = "PEARLS"
        orders: list[Order] = []
        order_depth: OrderDepth = state.order_depths[product]

        buyable_volume = self.pos_limit[product] - self.pos[product]
        sorted_sellorders = collections.OrderedDict(sorted(order_depth.sell_orders.items()))
        #for price, volume in sorted_sellorders.items():
        #    print(price, volume)
        for price, volume in sorted_sellorders.items():
            if price >= 10000 or buyable_volume == 0:
                break
            #print("volume", volume)
            buy_volume = min(buyable_volume, -volume)
            #print("buy_volume", buy_volume)
            buyable_volume -= buy_volume
            #print("buyable_volume", buyable_volume)
            #print("BUY", product, str(buy_volume) + "x", price)
            orders.append(Order(product, price, buy_volume))

        sellable_volume = -self.pos_limit[product] - self.pos[product]
        sorted_buyorders = collections.OrderedDict(sorted(order_depth.buy_orders.items(), reverse=True))
        #for price, volume in sorted_buyorders.items():
        #    print(price, volume)
        for price, volume in sorted_buyorders.items():
            if price <= 10000 or sellable_volume == 0:
                break
            sell_volume = max(sellable_volume, -volume)
            sellable_volume -= sell_volume
            print("SELL", product, str(sell_volume) + "x", price)
            orders.append(Order(product, price, sell_volume))

        result[product] = orders

        # Trading Bananas
        product = "BANANAS"
        orders: list[Order] = []
        order_depth: OrderDepth = state.order_depths[product]
        
        best_ask = min(order_depth.sell_orders.keys()) if len(
            order_depth.sell_orders) != 0 else None
        best_ask_volume = order_depth.sell_orders[best_ask] if best_ask is not None else None
        best_bid = max(order_depth.buy_orders.keys()) if len(
            order_depth.buy_orders) != 0 else None
        best_bid_volume = order_depth.buy_orders[best_bid] if best_bid is not None else None
        avg = (best_bid + best_ask) / \
            2 if best_bid is not None and best_ask is not None else None
        
        if avg is not None:
            self.sma[product].append(avg)
            if len(self.sma[product]) != 0:
                if len(self.sma[product]) < 7:
                    acceptable_price = np.array(self.sma[product]).mean()
                else:
                    acceptable_price = np.array(self.sma[product])[-7:].mean()
        else:
            acceptable_price = 5000

        if acceptable_price is not None and best_ask < acceptable_price:
            if best_ask_volume is not None:
                buyable_volume = min(-best_ask_volume, self.pos_limit[product] - self.pos[product])
            else:
                buyable_volume = self.pos_limit[product] - self.pos[product]

            if buyable_volume > 0:
                print("BUY", product, str(buyable_volume) + "x", best_ask)
                orders.append(Order(product, best_ask, buyable_volume))

        if acceptable_price is not None and best_bid > acceptable_price:
            if best_bid_volume is not None:
                sellable_volume = max(-best_bid_volume, -self.pos_limit[product] - self.pos[product])
            else:
                sellable_volume = -self.pos_limit[product] - self.pos[product]

            if sellable_volume < 0:
                print("SELL", product, str(sellable_volume) + "x", best_bid)
                orders.append(Order(product, best_bid, sellable_volume))

        result[product] = orders

        # Pair trading between COCONUTS and PINA_COLADAS
        print("Current Coconut Position", self.pos["COCONUTS"])
        print("Current Pina Position", self.pos["PINA_COLADAS"])
        orders_coconut: list[Order] = []
        orders_pina = []
        order_depth_coconut = state.order_depths["COCONUTS"]
        best_ask_coconut, best_ask_volume_coconut, best_bid_coconut, best_bid_volume_coconut, avg_coconut = self.get_order_book_info(order_depth_coconut)
        order_depth_pina = state.order_depths["PINA_COLADAS"]
        best_ask_pina, best_ask_volume_pina, best_bid_pina, best_bid_volume_pina, avg_pina = self.get_order_book_info(order_depth_pina)
        print("Coconuts Best Bid at",best_bid_volume_coconut,"x",best_bid_coconut)
        print("Coconuts Best Ask at",best_ask_volume_coconut,"x",best_ask_coconut)
        
        print("Pina Best Bid at",best_bid_volume_pina,"x",best_bid_pina)
        print("Pina Best Ask at",best_ask_volume_pina,"x",best_ask_pina)
        
        buyable_volume_coconut = self.pos_limit["COCONUTS"] - self.pos["COCONUTS"] # We can only buy less than this number
        sellable_volume_coconut = -self.pos_limit["COCONUTS"] - self.pos["COCONUTS"] # This number is negative
        buyable_volume_pina = self.pos_limit["PINA_COLADAS"] - self.pos["PINA_COLADAS"]
        sellable_volume_pina = -self.pos_limit["PINA_COLADAS"] - self.pos["PINA_COLADAS"]
        
        print("Buy at most", buyable_volume_coconut, "Coconuts")
        print("Sell at most", -sellable_volume_coconut, "Coconuts")
        print("Buy at most", buyable_volume_pina, "Pinas")
        print("Sell at most", -sellable_volume_pina, "Pinas")
        
        # compute normed price difference
        if avg_coconut is not None and avg_pina is not None:
            current_ratio = avg_coconut / avg_pina
            self.ratio.append(current_ratio)
        if avg_coconut is not None and avg_pina is not None and len(self.ratio) >= 30:
            window1 = 5
            window2 = 30
            ma1 = np.array(self.ratio)[-window1:].mean()
            ma2 = np.array(self.ratio)[-window2:].mean()
            std = np.array(self.ratio)[-window2:].std()
            zscore = (ma1 - ma2)/std
            print("ZSCORE",zscore)
            
            if zscore < -1:
                # Sell coconut, Buy pina
                # The four numbers below are positive
                max_coconut_sell = -min(best_ask_volume_coconut,sellable_volume_coconut)
                max_pina_buy = min(best_bid_volume_pina,buyable_volume_pina)
                if max_coconut_sell > max_pina_buy*current_ratio:
                    volume_coconut_sell = round(max_pina_buy*current_ratio)
                    volume_pina_buy = max_pina_buy
                else:
                    volume_coconut_sell = max_coconut_sell
                    volume_pina_buy = round(max_coconut_sell/current_ratio)
                orders_coconut.append(Order("COCONUTS",best_ask_coconut,-volume_coconut_sell))
                orders_pina.append(Order("PINA_COLADAS",best_bid_pina,volume_pina_buy))
                print("SELL COCONUTS", -volume_coconut_sell,"x",best_ask_coconut)
                print("BUY PINAS", volume_pina_buy,"x",best_bid_pina)
                
            if zscore > 1:
                # Sell pina, Buy coconut
                # The four numbers below are positive
                max_coconut_buy = min(best_bid_volume_coconut,buyable_volume_coconut)
                max_pina_sell = -min(best_ask_volume_pina,sellable_volume_pina)
                volume_pina_sell = min(max_pina_sell,round(max_coconut_buy/current_ratio))
                volume_coconut_buy = min(round(max_pina_sell*current_ratio), max_coconut_buy)
                if max_coconut_buy > max_pina_sell*current_ratio:
                    volume_coconut_buy = round(max_pina_sell*current_ratio)
                    volume_pina_sell = max_pina_sell
                else:
                    volume_coconut_buy = max_coconut_buy
                    volume_pina_sell = round(max_coconut_buy/current_ratio)
                orders_coconut.append(Order("COCONUTS",best_bid_coconut,volume_coconut_buy))
                orders_pina.append(Order("PINA_COLADAS",best_ask_pina,-volume_pina_sell))
                print("SELL PINAS", -volume_pina_sell,"x",best_ask_pina)
                print("BUY COCONUTS", volume_coconut_buy,"x",best_bid_coconut)
                
            # exit signal
            if abs(zscore) < 0.6:
                if self.pos["COCONUTS"] < 0: #Buy coconuts
                    orders_coconut.append(Order("COCONUTS",best_bid_coconut,-self.pos["COCONUTS"]))
                    print("BUY COCONUTS",-self.pos["COCONUTS"],"x",best_bid_coconut)
                
                if self.pos["COCONUTS"] > 0: #Sell coconuts
                    orders_coconut.append(Order("COCONUTS",best_ask_coconut,-self.pos["COCONUTS"]))
                    print("SELL COCONUTS",-self.pos["COCONUTS"],"x",best_ask_coconut)
                    
                if self.pos["PINA_COLADAS"] < 0: #Buy pinas
                    orders_pina.append(Order("PINA_COLADAS",best_bid_pina,-self.pos["PINA_COLADAS"]))
                    print("BUY PINAS",-self.pos["PINA_COLADAS"],"x",best_bid_pina)
                
                if self.pos["PINA_COLADAS"] > 0: #Sell pinas
                    orders_pina.append(Order("PINA_COLADAS",best_ask_pina,-self.pos["PINA_COLADAS"]))
                    print("SELL PINAS",-self.pos["PINA_COLADAS"],"x",best_ask_pina)
                
            # Add all the above orders to the result dict
            result["COCONUTS"] = orders_coconut
            result["PINA_COLADAS"] = orders_pina

        return result