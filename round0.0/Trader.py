from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order
import numpy as np


class Trader:
    def __init__(self):
        self.sma_PEARLS = np.array([])
        self.pos_limit_PEARLS = 20
        self.sma_BANANAS = np.array([])
        self.pos_limit_BANANAS = 20

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        """
        Only method required. It takes all buy and sell orders for all symbols as an input,
        and outputs a list of orders to be sent
        """
        # Initialize the method output dict as an empty dict
        result = {}

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

            # Position limit
            position = state.position[product]

            if product == 'PEARLS' and avg is not None:
                self.sma_PEARLS.append(avg)
                acceptable_price = self.sma_PEARLS.mean() if len(self.sma_PEARLS) > 1 else None
                self.pos_limit = self.pos_limit_PEARLS
            elif product == 'BANANAS' and avg is not None:
                self.sma_BANANAS.append(avg)
                acceptable_price = self.sma_BANANAS.mean() if len(self.sma_BANAS) > 1 else None
                self.pos_limit = self.pos_limit_BANANAS

            if acceptable_price is not None and best_ask < acceptable_price:
                buyable_volume = min(-best_ask_volume,
                                     self.pos_limit - position)
                print("BUY", str(buyable_volume) + "x", best_ask)
                orders.append(
                    Order(product, best_ask, buyable_volume))

            if acceptable_price is not None and best_bid > acceptable_price:
                sellable_volume = max(-best_bid_volume, -
                                      self.pos_limit-self.pos_limit)
                print("SELL", str(sellable_volume) + "x", best_bid)
                orders.append(
                    Order(product, best_bid, sellable_volume))

            # Add all the above orders to the result dict
            result[product] = orders

        return result
