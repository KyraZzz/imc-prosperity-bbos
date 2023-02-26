# imc-prosperity-bbos
## Format
- class `Trader`:
  - method `run`:
    - can either actively seek for a buy/sell order according to orderbook or put a waiting buy/sell order
    - can long or short, restricted by per project position limits
- Simulation environment:
  - invoke `run` in #iterations with `TradingState` object
  - `TradingState` object: 
    - an overview of all previous trades (i.e., entire market) since last iteration
    - per product overview of outstanding buy and sell orders