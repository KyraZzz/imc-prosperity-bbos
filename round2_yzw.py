import collections
from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order
import numpy as np


class Trader:
    def __init__(self):
        self.pos_limit = {"PINA_COLADAS": 20, "COCONUTS": 20}
        self.pos = {"PINA_COLADAS": 0, "COCONUTS": 0}
        self.last_timestamp = {"PINA_COLADAS": 0, "COCONUTS": 0}
        self.price_difference = []

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

        orders_pc: list[Order] = []
        orders_c: list[Order] = []
        order_depth_pc: OrderDepth = state.order_depths["PINA_COLADAS"]
        order_depth_c: OrderDepth = state.order_depths["COCONUTS"]
        # Sort the sell orders and buy orders
        best_ask_pc = min(order_depth_pc.sell_orders.keys()) if len(
            order_depth_pc.sell_orders) != 0 else None
        best_ask_volume_pc = order_depth_pc.sell_orders[best_ask_pc] if best_ask_pc is not None else None
        best_bid_pc = max(order_depth_pc.buy_orders.keys()) if len(
            order_depth_pc.buy_orders) != 0 else None
        best_bid_volume_pc = order_depth_pc.buy_orders[best_bid_pc] if best_bid_pc is not None else None
        avg_pc = (best_bid_pc + best_ask_pc) / \
            2 if best_bid_pc is not None and best_ask_pc is not None else None
        
        best_ask_c = min(order_depth_c.sell_orders.keys()) if len(
            order_depth_c.sell_orders) != 0 else None
        best_ask_volume_c = order_depth_c.sell_orders[best_ask_c] if best_ask_c is not None else None
        best_bid_c = max(order_depth_c.buy_orders.keys()) if len(
            order_depth_c.buy_orders) != 0 else None
        best_bid_volume_c = order_depth_c.buy_orders[best_bid_c] if best_bid_c is not None else None
        avg_c = (best_bid_c + best_ask_c) / \
            2 if best_bid_c is not None and best_ask_c is not None else None#
        
        self.price_difference.append(avg_pc - avg_c)

        if self.price_difference[-1] is not None and self.price_difference[-1] > 7010: #sell pina colada and buy coconuts
            buyable_volume = min(-best_ask_volume_c,
                                     self.pos_limit['COCONUTS'] - self.pos['COCONUTS'])
            sellable_volume = max(-best_bid_volume_pc, -
                                      self.pos_limit['PINA_COLADAS'] - self.pos['PINA_COLADAS'])
            expected_volume = min(buyable_volume, abs(sellable_volume))

            if buyable_volume > 0 and sellable_volume < 0: #buy coconut
                print("BUY", "COCONUTS", str(expected_volume) + "x", best_ask_c)
                orders_c.append(Order("COCONUTS", best_ask_c,expected_volume ))
                print("SELL", "PINA_COLADAS", str(expected_volume) + "x", best_bid_pc)
                orders_pc.append(Order("PINA_COLADAS", best_bid_pc,-expected_volume ))
                print("****************")
        if self.price_difference[-1] is not None and self.price_difference[-1] < 6990:#buy pina colada and sell coconuts
            buyable_volume = min(-best_ask_volume_pc,
                                     self.pos_limit['PINA_COLADAS'] - self.pos['PINA_COLADAS'])
            sellable_volume = max(-best_bid_volume_c, -
                                      self.pos_limit['COCONUTS'] - self.pos['COCONUTS'])
            expected_volume = min(buyable_volume, abs(sellable_volume))

            if buyable_volume > 0 and sellable_volume < 0: #buy coconut
                print("BUY", "PINA_COLADAS", str(expected_volume) + "x", best_ask_pc)
                orders_pc.append(Order("PINA_COLADAS", best_ask_pc,expected_volume))
                print("SELL", "COCONUTS", str(expected_volume) + "x", best_bid_c)
                orders_c.append(Order("COCONUTS", best_bid_c,-expected_volume ))
                print("****************")            
        result['PINA_COLADAS'] = orders_pc
        result['COCONUTS'] = orders_c

        return result