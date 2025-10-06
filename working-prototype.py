from AlgorithmImports import *

class OptionsDataGraphAlgorithm(QCAlgorithm):
    
    def initialize(self):
        self.set_start_date(2020, 6, 1)
        self.set_end_date(2020, 6, 8)
        self.set_cash(100000)
        
        # Add SPY options
        option = self.add_option("SPY")
        self.option_symbol = option.symbol
        option.set_filter(-10, 10, 0, 60)
        
        # Create charts explicitly
        options_chart = Chart("Options Prices")
        options_chart.add_series(Series("ATM Call", SeriesType.LINE, 0))
        options_chart.add_series(Series("ATM Put", SeriesType.LINE, 0))
        options_chart.add_series(Series("Underlying", SeriesType.LINE, 1))
        self.add_chart(options_chart)
        
        greeks_chart = Chart("Implied Volatility")
        greeks_chart.add_series(Series("Call IV", SeriesType.LINE, 0))
        greeks_chart.add_series(Series("Put IV", SeriesType.LINE, 0))
        self.add_chart(greeks_chart)
        
    def on_data(self, slice):
        if self.option_symbol not in slice.option_chains:
            return
            
        chain = slice.option_chains[self.option_symbol]
        if len(chain) == 0:
            return
        
        underlying_price = chain.underlying.price
        calls = [c for c in chain if c.right == OptionRight.CALL]
        puts = [c for c in chain if c.right == OptionRight.PUT]
        
        if len(calls) > 0 and len(puts) > 0:
            # Find ATM contracts
            atm_call = min(calls, key=lambda x: abs(x.strike - underlying_price))
            atm_put = min(puts, key=lambda x: abs(x.strike - underlying_price))
            
            # Plot to the charts we created
            self.plot("Options Prices", "ATM Call", atm_call.last_price)
            self.plot("Options Prices", "ATM Put", atm_put.last_price)
            self.plot("Options Prices", "Underlying", underlying_price)
            self.plot("Implied Volatility", "Call IV", atm_call.implied_volatility * 100)
            self.plot("Implied Volatility", "Put IV", atm_put.implied_volatility * 100)