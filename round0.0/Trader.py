from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order
import numpy as np


class Trader:
    def __init__(self):
        self.pos_limit = {"PEARLS": 20, "BANANAS": 20}
        self.pos = {"PEARLS": 0, "BANANAS": 0}
        self.sma = {"PEARLS": [], "BANANAS": []}

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        """
        Only method required. It takes all buy and sell orders for all symbols as an input,
        and outputs a list of orders to be sent
        """
        # Initialize the method output dict as an empty dict
        result = {}

        # Update positions
        for product, trades in state.own_trades.items():
            pos_delta = 0
            for trade in trades:
                if trade.buyer == "SUBMISSION":
                    # We bought product
                    pos_delta += trade.quantity
                else:
                    pos_delta -= trade.quantity
            self.pos[product] += pos_delta

        # Iterate over all the keys (the available products) contained in the order depths
        for product in state.order_depths.keys():
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
                acceptable_price = np.array(self.sma[product]).mean() if len(
                    self.sma[product]) != 0 else None

            if acceptable_price is not None and best_ask < acceptable_price:
                buyable_volume = min(-best_ask_volume,
                                     self.pos_limit[product] - self.pos[product])
                print("BUY", str(buyable_volume) + "x", best_ask)
                orders.append(
                    Order(product, best_ask, buyable_volume))

            if acceptable_price is not None and best_bid > acceptable_price:
                sellable_volume = max(-best_bid_volume, -
                                      self.pos_limit[product] - self.pos[product])
                print("SELL", str(sellable_volume) + "x", best_bid)
                orders.append(
                    Order(product, best_bid, sellable_volume))

            # Add all the above orders to the result dict
            result[product] = orders

        return result
