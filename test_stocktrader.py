"""
This is just some testing code for the stocktrader module.
Feel free to modify and use for simulating the stockmarket
"""
import stocktrader as s

s.loadAllStocks()

s.loadPortfolio()

s.valuatePortfolio("9.12.2014", True)

s.sellAll('10.12.2014', True)

print(s.valuatePortfolio("16.12.2014"))
