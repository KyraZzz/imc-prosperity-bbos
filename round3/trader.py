import collections
from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order
import numpy as np


class Trader:
    def __init__(self):
        self.pos_limit = {"PEARLS": 20, "BANANAS": 20, "COCONUTS": 600,
                          "PINA_COLADAS": 300, "BERRIES": 250, "DIVING_GEAR": 50}
        self.pos = {"PEARLS": 0, "BANANAS": 0, "COCONUTS": 0,
                    "PINA_COLADAS": 0, "BERRIES": 0, "DIVING_GEAR": 0}
        self.sma = {"PEARLS": [], "BANANAS": [], "BERRIES": []}
        self.last_timestamp = {"PEARLS": 0, "BANANAS": 0, "COCONUTS": 0,
                               "PINA_COLADAS": 0, "BERRIES": 0, "DIVING_GEAR": 0}
        self.diffs = []
        self.entered = 0
        self.pc_midprices = []
        self.c_midprices = []

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

    def trade_pearls(self, state: TradingState):
        product = "PEARLS"
        orders: list[Order] = []
        order_depth: OrderDepth = state.order_depths[product]

        buyable_volume = self.pos_limit[product] - self.pos[product]
        sorted_sellorders = collections.OrderedDict(
            sorted(order_depth.sell_orders.items()))
        for price, volume in sorted_sellorders.items():
            print(price, volume)
        for price, volume in sorted_sellorders.items():
            if price >= 10000 or buyable_volume == 0:
                break
            print("volume", volume)
            buy_volume = min(buyable_volume, -volume)
            print("buy_volume", buy_volume)
            buyable_volume -= buy_volume
            print("buyable_volume", buyable_volume)
            print("BUY", product, str(buy_volume) + "x", price)
            orders.append(Order(product, price, buy_volume))

        sellable_volume = -self.pos_limit[product] - self.pos[product]
        sorted_buyorders = collections.OrderedDict(
            sorted(order_depth.buy_orders.items(), reverse=True))
        for price, volume in sorted_buyorders.items():
            print(price, volume)
        for price, volume in sorted_buyorders.items():
            if price <= 10000 or sellable_volume == 0:
                break
            sell_volume = max(sellable_volume, -volume)
            sellable_volume -= sell_volume
            print("SELL", product, str(sell_volume) + "x", price)
            orders.append(Order(product, price, sell_volume))

        return orders

    def trade_bananas(self, state: TradingState):
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

        # if avg is not None:
        #     if self.banana_acceptable_price == 0:
        #         self.banana_acceptable_price = avg
        #     else: self.banana_acceptable_price = self.banana_acceptable_price * 0.8 + avg * 0.2
        #     acceptable_price = self.banana_acceptable_price
        # else: acceptable_price = 4990
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

        return orders

    def pair_trade(self, state: TradingState):
        # Pair trading between COCONUTS and PINA_COLADAS
        orders_coconut: list[Order] = []
        orders_pina = []
        order_depth_coconut = state.order_depths["COCONUTS"]
        best_ask_coconut, best_ask_volume_coconut, best_bid_coconut, best_bid_volume_coconut, avg_coconut = self.get_order_book_info(
            order_depth_coconut)
        order_depth_pina = state.order_depths["PINA_COLADAS"]
        best_ask_pina, best_ask_volume_pina, best_bid_pina, best_bid_volume_pina, avg_pina = self.get_order_book_info(
            order_depth_pina)
        hedge_ratio = 8/15
        THRESHOLD = 2e-3
        fair_price_pina = 15000 - 3000
        fair_price_coconuts = 8000 - 3000
        MAX_SLOT = 10
        print(
            f"best_ask_coconut: {best_ask_coconut} * {best_ask_volume_coconut}, best_bid_coconut: {best_bid_coconut} * {best_bid_volume_coconut}, avg_coconut: {avg_coconut} ")
        print(
            f"best_ask_pina: {best_ask_pina} * {best_ask_volume_pina}, best_bid_pina: {best_bid_pina} * {best_bid_volume_pina}, avg_pina: {avg_pina}")

        # compute normed price difference
        if avg_coconut is not None and avg_pina is not None:
            # entry signal
            if (best_bid_pina - fair_price_pina) - (best_ask_coconut - fair_price_coconuts) >= THRESHOLD * (best_ask_coconut - fair_price_coconuts) and best_ask_coconut != 0:
                # sell/hit bid in PINA, buy/take offer in COCONUT
                bid_product = "COCONUTS"
                ask_product = "PINA_COLADAS"
                bid_volume = min(MAX_SLOT, -best_ask_volume_coconut,
                                 self.pos_limit[bid_product] - self.pos[bid_product])
                ask_volume = min(MAX_SLOT, best_bid_volume_pina,
                                 self.pos_limit[ask_product] + self.pos[ask_product])
                volume = min(bid_volume, ask_volume)
                if volume > 0:
                    print("BUY", bid_product, str(
                        volume) + "x", best_ask_coconut)
                    orders_coconut.append(
                        Order(bid_product, best_ask_coconut, volume))
                    print("SELL", ask_product, str(
                        -volume) + "x", best_bid_pina)
                    orders_pina.append(
                        Order(ask_product, best_bid_pina, -volume))

            elif (best_bid_coconut - fair_price_coconuts) - (best_ask_pina - fair_price_pina) >= THRESHOLD * (best_ask_pina - fair_price_pina) and best_ask_pina != 0:
                # hit bid in COCONUT, take offer in PINA
                bid_product = "PINA_COLADAS"
                ask_product = "COCONUTS"
                bid_volume = min(MAX_SLOT, -best_ask_volume_pina,
                                 self.pos_limit[bid_product] - self.pos[bid_product])
                ask_volume = min(MAX_SLOT, best_bid_volume_coconut,
                                 self.pos_limit[ask_product] + self.pos[ask_product])
                volume = min(int(bid_volume / hedge_ratio), ask_volume)
                if volume > 0:
                    print("BUY", bid_product, str(
                        int(hedge_ratio * volume)) + "x", best_ask_pina)
                    orders_pina.append(
                        Order(bid_product, best_ask_pina, int(hedge_ratio * volume)))
                    print("SELL", ask_product, str(
                        -volume) + "x", best_bid_coconut)
                    orders_coconut.append(
                        Order(ask_product, best_bid_coconut, -volume))

            # when we have long COCONUT and we need to sell it
            if self.pos["COCONUTS"] > 0 and best_bid_coconut - fair_price_coconuts > best_ask_pina - fair_price_pina:
                bid_product = "PINA_COLADAS"
                ask_product = "COCONUTS"
                bid_volume = min(-best_ask_volume_pina,
                                 self.pos_limit[bid_product] - self.pos[bid_product])
                ask_volume = min(best_bid_volume_coconut,
                                 self.pos_limit[ask_product] + self.pos[ask_product])
                volume = min(int(hedge_ratio * bid_volume), ask_volume)
                if volume > 0:
                    print("SELL", ask_product, str(-volume) +
                          "x", best_bid_coconut)
                    orders_coconut.append(
                        Order(ask_product, best_bid_coconut, -volume))
                    print("BUY", bid_product, str(
                        int(volume / hedge_ratio)) + "x", best_ask_pina)
                    orders_pina.append(
                        Order(bid_product, best_ask_pina, int(volume / hedge_ratio)))

            # when we have short COCONUT and we need to buy it
            elif self.pos["COCONUTS"] < 0 and best_bid_pina - fair_price_pina > best_ask_coconut - fair_price_coconuts:
                bid_product = "COCONUTS"
                ask_product = "PINA_COLADAS"
                bid_volume = min(-best_ask_volume_coconut,
                                 self.pos_limit[bid_product] - self.pos[bid_product])
                ask_volume = min(best_bid_volume_pina,
                                 self.pos_limit[ask_product] + self.pos[ask_product])
                volume = min(bid_volume, ask_volume)
                if volume > 0:
                    print("BUY", bid_product, str(
                        volume) + "x", best_ask_coconut)
                    orders_coconut.append(
                        Order(bid_product, best_ask_coconut, volume))
                    print("SELL", ask_product, str(
                        -volume) + "x", best_bid_pina)
                    orders_pina.append(
                        Order(ask_product, best_bid_pina, -volume))

        return orders_coconut, orders_pina

    def trade_mayberry(self, state: TradingState):
        orders = []
        order_depth = state.order_depths["BERRIES"]
        best_ask, best_ask_volume, best_bid, best_bid_volume, avg = self.get_order_book_info(
            order_depth)
        if avg is not None:
            self.sma["BERRIES"].append(avg)
            if len(self.sma["BERRIES"]) > 7:
                acceptable_price = np.array(
                    self.sma["BERRIES"])[-7:].mean()
            else:
                acceptable_price = 3900

        if best_ask < acceptable_price:
            if best_ask_volume is not None:
                buyable_volume = min(-best_ask_volume,
                                     self.pos_limit["BERRIES"] - self.pos["BERRIES"])
            else:
                buyable_volume = self.pos_limit["BERRIES"] - \
                    self.pos["BERRIES"]

            if buyable_volume > 0:
                print("BUY", "BERRIES", str(buyable_volume) + "x", best_ask)
                orders.append(Order("BERRIES", best_ask, buyable_volume))

        if best_bid > acceptable_price:
            if best_bid_volume is not None:
                sellable_volume = max(-best_bid_volume, -
                                      self.pos_limit["BERRIES"] - self.pos["BERRIES"])
            else:
                sellable_volume = - \
                    self.pos_limit["BERRIES"] - self.pos["BERRIES"]

            if sellable_volume < 0:
                print("SELL", "BERRIES", str(sellable_volume) + "x", best_bid)
                orders.append(Order("BERRIES", best_bid, sellable_volume))

        return orders

    def trade_diving_gears(self, state):
        pass

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        """
        Only method required. It takes all buy and sell orders for all symbols as an input,
        and outputs a list of orders to be sent
        """
        # Initialize the method output dict as an empty dict
        result = {}

        # Update positions
        for product, trades in state.own_trades.items():
            if len(trades) == 0 or trades[0].timestamp == self.last_timestamp[product]:
                continue
            pos_delta = 0
            for trade in trades:
                print(
                    f"buyer: {trade.buyer}, seller: {trade.seller}, price: {trade.price}, quantity: {trade.quantity}, symbol: {trade.symbol}")
                if trade.buyer == "SUBMISSION":
                    # We bought product
                    pos_delta += trade.quantity
                    # self.profit -= trade.price * trade.quantity
                elif trade.seller == "SUBMISSION":
                    pos_delta -= trade.quantity
                    # self.profit += trade.price * trade.quantity
            self.pos[product] += pos_delta
            self.last_timestamp[product] = trades[0].timestamp

        # result["PEARLS"] = self.trade_pearls(state)

        # result["BANANAS"] = self.trade_bananas(state)

        result["COCONUTS"], result["PINA_COLADAS"] = self.pair_trade(state)

        # result["BERRIES"] = self.trade_mayberry(state)

        return result
