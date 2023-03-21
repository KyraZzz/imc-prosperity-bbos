import collections
from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order
import numpy as np


class Trader:
    def __init__(self):
        self.pos_limit = {"PEARLS": 20, "BANANAS": 20}
        self.pos = {"PEARLS": 0, "BANANAS": 0}
        self.sma = {"PEARLS": [], "BANANAS": []}
        self.last_timestamp = {"PEARLS": 0, "BANANAS": 0}

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        """
        Only method required. It takes all buy and sell orders for all symbols as an input,
        and outputs a list of orders to be sent
        """
        # Initialize the method output dict as an empty dict
        result = {}
        print("****************")

        # Update positions
        for product, trades in state.own_trades.items():
            if len(trades) == 0 or trades[0].timestamp == self.last_timestamp[product]:
                continue
            pos_delta = 0
            for trade in trades:
                print(trade.buyer, trade.seller, trade.price,
                      trade.quantity, trade.symbol)
                if trade.buyer == "SUBMISSION":
                    # We bought product
                    pos_delta += trade.quantity
                    # self.profit -= trade.price * trade.quantity
                elif trade.seller == "SUBMISSION":
                    pos_delta -= trade.quantity
                    # self.profit += trade.price * trade.quantity
            self.pos[product] += pos_delta
            self.last_timestamp[product] = trades[0].timestamp

        # product = "PEARLS"
        # orders: list[Order] = []
        # order_depth: OrderDepth = state.order_depths[product]

        # buyable_volume = self.pos_limit[product] - self.pos[product]
        # sorted_sellorders = collections.OrderedDict(sorted(order_depth.sell_orders.items()))
        # for price,volume in sorted_sellorders.items():
        #     print(price, volume)
        # for price, volume in sorted_sellorders.items():
        #     if price >= 10000 or buyable_volume == 0:
        #         break
        #     print("volume", volume)
        #     buy_volume = min(buyable_volume, -volume)
        #     print("buy_volume", buy_volume)
        #     buyable_volume -= buy_volume
        #     print("buyable_volume", buyable_volume)
        #     print("BUY", product, str(buy_volume) + "x", price)
        #     orders.append(Order(product, price, buy_volume))

        # sellable_volume = -self.pos_limit[product] - self.pos[product]
        # sorted_buyorders = collections.OrderedDict(sorted(order_depth.buy_orders.items(), reverse = True))
        # for price,volume in sorted_buyorders.items():
        #     print(price, volume)
        # for price, volume in sorted_buyorders.items():
        #     if price <= 10000 or sellable_volume == 0:
        #         break
        #     sell_volume = max(sellable_volume, -volume)
        #     sellable_volume -= sell_volume
        #     print("SELL", product, str(sell_volume) + "x", price)
        #     orders.append(Order(product, price, sell_volume))

        # result[product] = orders

        # Iterate over all the keys (the available products) contained in the order depths
        product = "BANANAS"
        # Initialise the list of Orders to be sent as an empty list
        orders: list[Order] = []

        # Obtain OrderDepth object for the product
        order_depth: OrderDepth = state.order_depths[product]
        # Sort the sell orders and buy orders
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
            acceptable_price = 4990

        if acceptable_price is not None and best_ask < acceptable_price:
            if best_ask_volume is not None:
                buyable_volume = min(-best_ask_volume,
                                     self.pos_limit[product] - self.pos[product])
            else:
                buyable_volume = self.pos_limit[product] - self.pos[product]

            if buyable_volume > 0:
                print("BUY", product, str(buyable_volume) + "x", best_ask)
                orders.append(Order(product, best_ask, buyable_volume))

        if acceptable_price is not None and best_bid > acceptable_price:
            if best_bid_volume is not None:
                sellable_volume = max(-best_bid_volume, -
                                      self.pos_limit[product] - self.pos[product])
            else:
                sellable_volume = -self.pos_limit[product] - self.pos[product]

            if sellable_volume < 0:
                print("SELL", product, str(sellable_volume) + "x", best_bid)
                orders.append(Order(product, best_bid, sellable_volume))

        # Add all the above orders to the result dict
        result[product] = orders

        return result
