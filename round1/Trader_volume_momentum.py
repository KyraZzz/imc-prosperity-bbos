from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order
import numpy as np


class Trader:
    def __init__(self):
        self.pos_limit = {"PEARLS": 20, "BANANAS": 20}
        self.pos = {"PEARLS": 0, "BANANAS": 0}
        self.profit = 0
        self.pnl = 0

    def compute_weighted_mean(self, orders, reverse=False):
        # sort the orders
        keys = np.array(list(orders.keys()))
        values = np.abs(np.array(list(orders.values())))
        key_sort_idx = np.argsort(keys)
        if reverse:
            key_sort_idx = key_sort_idx[::-1]
        sorted_keys = keys[key_sort_idx]
        sorted_values = values[key_sort_idx]
        # assume prices = np.array([123, 124, 127, 129, 134])
        # prices_diff = array([1, 3, 2, 5])
        # weights = array([1]) + 1/(1+cum(prices_diff))
        price_diff = np.diff(sorted_keys)
        weights = np.concatenate(
            [np.array([1]), 1/(1 + np.cumsum(price_diff))])

        print(f"keys: {keys}, values: {values}, weights: {weights}")

        # return weight mean
        return np.mean(sorted_values * weights), sorted_keys, sorted_values

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
                    self.profit -= trade.price * trade.quantity
                elif trade.seller == "SUBMISSION":
                    pos_delta -= trade.quantity
                    self.profit += trade.price * trade.quantity
            self.pos[product] += pos_delta
        print(f"Current profit {self.profit}")

        # Iterate over all the keys (the available products) contained in the order depths
        product = "BANANAS"
        # Initialise the list of Orders to be sent as an empty list
        orders: list[Order] = []

        # Obtain OrderDepth object for the product
        order_depth: OrderDepth = state.order_depths[product]

        new_mean_bid, sorted_bid_price, sorted_bid_volume = self.compute_weighted_mean(order_depth.buy_orders) if len(
            order_depth.buy_orders) != 0 else None
        new_mean_ask, sorted_ask_price, sorted_ask_volume = self.compute_weighted_mean(order_depth.sell_orders, reverse=True) if len(
            order_depth.sell_orders) != 0 else None
        delta = new_mean_bid - \
            new_mean_ask if new_mean_bid is not None and new_mean_ask is not None else None
        print(
            f"Weighted mean bid: {new_mean_bid}, weighted mean ask: {new_mean_ask}, delta: {delta}")

        if delta is not None and delta > 0:
            # heavier bid demands
            best_bid = sorted_bid_price[0]
            buyable_volume = min(sorted_bid_volume[0],
                                 self.pos_limit[product] - self.pos[product])
            if buyable_volume > 0:
                print("BUY", product, str(buyable_volume) + "x", best_bid)
                orders.append(Order(product, best_bid, buyable_volume))

        if delta is not None and delta < 0:
            # heavier ask demands
            best_ask = sorted_ask_price[0]
            sellable_volume = min(
                sorted_ask_volume[0], self.pos_limit[product] + self.pos[product])
            if sellable_volume > 0:
                print("SELL", product, str(-sellable_volume) + "x", best_ask)
                orders.append(Order(product, best_ask, -sellable_volume))

        # Add all the above orders to the result dict
        result[product] = orders

        return result
