import collections
from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order, ProsperityEncoder, Symbol
import numpy as np
import json
from typing import Any

LOT_SIZE = 10
class Logger:
    def __init__(self) -> None:
        self.logs = ""

    def print(self, *objects: Any, sep: str = " ", end: str = "\n") -> None: #The * symbol indicates that an arbitrary number of # arguments can be passed to `args
        self.logs += sep.join(map(str, objects)) + end

    def flush(self, state: TradingState, orders: dict[Symbol, list[Order]]) -> None:
        print(json.dumps({
            "state": state,
            "orders": orders,
            "logs": self.logs,
        }, cls=ProsperityEncoder, separators=(",", ":"), sort_keys=True))
        self.logs = ""
    #Typically this means that the data will be copied from the program buffer to the operating system buffer.


logger = Logger()


class Trader:
    def __init__(self):
        self.pos_limit = {"PEARLS": 20, "BANANAS": 20, "COCONUTS": 600,
                          "PINA_COLADAS": 300, "BERRIES": 250, "DIVING_GEAR": 50, 
                          "BAGUETTE": 150, "DIP":300, "UKULELE": 70, "PICNIC_BASKET":70}
        self.pos = {"PEARLS": 0, "BANANAS": 0, "COCONUTS": 0,
                    "PINA_COLADAS": 0, "BERRIES": 0, "DIVING_GEAR": 0, "BAGUETTE": 0, "DIP":0, "UKULELE": 0, "PICNIC_BASKET":0}
        self.sma = {"PEARLS": [], "BANANAS": [],
                    "BERRIES": [], "DIVING_GEAR": []}
        self.last_timestamp = {"PEARLS": 0, "BANANAS": 0, "COCONUTS": 0,
                               "PINA_COLADAS": 0, "BERRIES": 0, "DIVING_GEAR": 0, "BAGUETTE": 0, "DIP":0, "UKULELE": 0, "PICNIC_BASKET":0}
        self.diffs = []
        self.entered = 0
        self.combined_midprices = []
        self.basket_midprices = []
        self.dolphin_sightings = []

    def get_order_book_info(self, order_depth):
        best_ask = min(order_depth.sell_orders.keys()) if len(
            order_depth.sell_orders) != 0 else None
        best_ask_volume = order_depth.sell_orders[best_ask] if best_ask is not None else None
        best_bid = max(order_depth.buy_orders.keys()) if len(
            order_depth.buy_orders) != 0 else None
        best_bid_volume = order_depth.buy_orders[best_bid] if best_bid is not None else None
        avg = (best_bid + best_ask) / \
            2 if best_bid is not None and best_ask is not None else None
        return best_ask, best_ask_volume, best_bid, best_bid_volume, avg

    def pair_trade(self, state: TradingState):
        # Pair trading between COCONUTS and PINA_COLADAS
        order_baguette: list[Order] = []
        order_dip = []
        order_ukulele = []
        order_picnic = []
        order_depth_baguette = state.order_depths["BAGUETTE"]
        order_depth_dip = state.order_depths["DIP"]
        order_depth_ukulele = state.order_depths["UKULELE"]
        order_depth_picnic = state.order_depths["PICNIC_BASKET"]
        best_ask_baguette, best_ask_volume_baguette, best_bid_baguette, best_bid_volume_baguette, avg_baguette = self.get_order_book_info(order_depth_baguette)
        best_ask_dip, best_ask_volume_dip, best_bid_dip, best_bid_volume_dip, avg_dip= self.get_order_book_info(order_depth_dip)
        best_ask_ukulele, best_ask_volume_ukulele, best_bid_ukulele, best_bid_volume_ukulele, avg_ukulele = self.get_order_book_info(order_depth_ukulele)
        best_ask_picnic, best_ask_volume_picnic, best_bid_picnic, best_bid_volume_picnic, avg_picnic = self.get_order_book_info(order_depth_picnic)
        best_ask_combined,best_bid_combined = 15*best_ask_baguette/7 + 30*best_ask_dip/7 + best_ask_ukulele, 15*best_bid_baguette/7 + 30*best_bid_dip/7 + best_bid_ukulele
        avg_combined = (best_ask_combined + best_bid_combined)/2
        # compute normed price difference
        print("entered = ", self.entered)

        if avg_combined is not None and avg_picnic is not None:
            self.combined_midprices.append(avg_combined)
            self.basket_midprices.append(avg_picnic)
            difference = avg_combined - avg_picnic
            self.diffs.append(difference)
            mean = np.array(self.diffs).mean()
            std = np.array(self.diffs).std()
            z = (difference - mean) / std
            print(difference, len(self.diffs), mean, std, z)
            if abs(z) < 0.2:
                print("AAAAAAAAAAAAAAAAAAAAAA")
                self.entered = 0
                product = "BAGUETTE"
                volume = self.pos["BAGUETTE"]
                print("BAGUETTE volume = ", volume)
                if volume > 0:
                    # sell all existing positions
                    print("SELL", product, str(-volume) + "x", best_bid_baguette)
                    order_baguette.append(
                        Order(product, best_bid_baguette, -volume))
                elif volume < 0:
                    # buy all existing positions
                    print("BUY", product, str(-volume) + "x", best_ask_baguette)
                    order_baguette.append(
                        Order(product, best_ask_baguette, -volume))

                product = "DIP"
                volume = self.pos["DIP"]
                if volume > 0:
                    # sell all existing positions
                    print("SELL", product, str(-volume) + "x", best_bid_dip)
                    order_dip.append(Order(product, best_bid_dip, -volume))
                elif volume < 0:
                    # buy all existing positions
                    print("BUY", product, str(-volume) + "x", best_ask_dip)
                    order_dip.append(Order(product, best_ask_dip, -volume))

                product = "UKULELE"
                volume = self.pos["UKULELE"]
                if volume > 0:
                    # sell all existing positions
                    print("SELL", product, str(-volume) + "x", best_bid_ukulele)
                    order_ukulele.append(Order(product, best_bid_ukulele, -volume))
                elif volume < 0:
                    # buy all existing positions
                    print("BUY", product, str(-volume) + "x", best_ask_ukulele)
                    order_ukulele.append(Order(product, best_ask_ukulele, -volume))

                product = "PICNIC_BASKET"
                volume = self.pos["PICNIC_BASKET"]
                if volume > 0:
                    # sell all existing positions
                    print("SELL", product, str(-volume) + "x", best_bid_picnic)
                    order_picnic.append(Order(product, best_bid_picnic, -volume))
                elif volume < 0:
                    # buy all existing positions
                    print("BUY", product, str(-volume) + "x", best_ask_picnic)
                    order_picnic.append(Order(product, best_ask_picnic, -volume))

            elif z > 1:
                print("BBBBBBBBBBBBBBBBBBBBBBBBB")
                # Combined overpriced, basket underpriced
                self.entered += 1
                bid_product = "PICNIC_BASKET"
                ask_product1 = "BAGUETTE"
                ask_product2 = "DIP"
                ask_product3 = "UKULELE"
                bid_volume = min(LOT_SIZE,
                                 self.pos_limit[bid_product] - self.pos[bid_product])
                ask_volume = -min(LOT_SIZE,
                                  int(7/15*(self.pos_limit[ask_product1] + self.pos[ask_product1])),
                                  int(7/30*(self.pos_limit[ask_product2] + self.pos[ask_product2])),
                                  self.pos_limit[ask_product3] + self.pos[ask_product3])
                volume = min(bid_volume, abs(ask_volume))
                bid_volume, ask_volume1, ask_volume2, ask_volume3 = volume, -int(15*volume/7), -int(30*volume/7), -volume
                # TODO: TREAT VOLUME SEPARATELY?
                if bid_volume > 0 and ask_volume < 0:
                    print("BUY", bid_product, str(
                        bid_volume) + "x", best_ask_picnic)
                    order_picnic.append(
                        Order(bid_product, best_ask_picnic, bid_volume))
                    print("SELL", ask_product1, str(
                        ask_volume1) + "x", best_bid_baguette)
                    order_baguette.append(
                        Order(ask_product1, best_bid_baguette, ask_volume1))
                    print("SELL", ask_product2, str(
                        ask_volume2) + "x", best_bid_dip)
                    order_dip.append(
                        Order(ask_product2, best_bid_dip, ask_volume2))
                    print("SELL", ask_product3, str(
                        ask_volume3) + "x", best_bid_ukulele)
                    order_ukulele.append(
                        Order(ask_product3, best_bid_ukulele, ask_volume3))
            elif z < -1:
                # basket overpriced, combined underpriced
                self.entered -= 1
                ask_product = "PICNIC_BASKET"
                bid_product1 = "BAGUETTE"
                bid_product2 = "DIP"
                bid_product3 = "UKULELE"
                bid_volume = min(LOT_SIZE,
                                  int(7/15*(self.pos_limit[bid_product1] - self.pos[bid_product1])),
                                  int(7/30*(self.pos_limit[bid_product2] - self.pos[bid_product2])),
                                  self.pos_limit[bid_product3] -self.pos[bid_product3])
                ask_volume = -min(LOT_SIZE,
                                  self.pos_limit[ask_product] + self.pos[ask_product])
                volume = min(bid_volume, abs(ask_volume))
                ask_volume, bid_volume1, bid_volume2, bid_volume3 = -volume, int(15*volume/7), int(30*volume/7), volume
                # TODO: TREAT VOLUME SEPARATELY?
                print("CCCCCCCCCCCCCCCCCCCCCCCC")
                if bid_volume > 0 and ask_volume < 0:                    
                    print("BUY", bid_product1, str(
                        bid_volume1) + "x", best_ask_baguette)
                    order_baguette.append(
                        Order(bid_product1, best_ask_baguette, bid_volume1))
                    print("BUY", bid_product2, str(
                        bid_volume2) + "x", best_ask_dip)
                    order_dip.append(
                        Order(bid_product2, best_ask_dip, bid_volume2))
                    print("BUY", bid_product3, str(
                        bid_volume3) + "x", best_ask_ukulele)
                    order_ukulele.append(
                        Order(bid_product3, best_ask_ukulele, bid_volume3))               
                    print("SELL", ask_product, str(
                        ask_volume) + "x", best_bid_picnic)
                    order_picnic.append(
                        Order(ask_product, best_bid_picnic, ask_volume))

        return order_baguette, order_dip, order_ukulele, order_picnic



    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        # Initialize the method output dict as an empty dict
        result = {}

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

        result["BAGUETTE"], result["DIP"],result["UKULELE"],result["PICNIC_BASKET"], = self.pair_trade(state)

        logger.flush(state, result)

        return result