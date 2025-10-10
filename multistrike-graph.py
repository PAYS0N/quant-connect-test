from AlgorithmImports import *
from datetime import datetime

# notes
# plots average of data over each day

class OptionsDataGraphAlgorithm(QCAlgorithm):
    def initialize(self):
        self.set_start_date(2024, 12, 1)
        self.set_end_date(2025, 2, 21)
        self.set_cash(100000)
        
        self.target_date = datetime(2025, 2, 21).date()
        self.target_strikes = [235]
        
        # Add AAPL options
        option = self.add_option("AAPL")
        self.option_symbol = option.symbol
        option.set_filter(-5, 5, 0, 90)
        
        # Track current day and accumulate data
        self.current_date = None
        self.daily_data = {}  # {strike: {'call_ivs': [], 'put_ivs': [], 'call_prices': [], 'put_prices': []}}
        
        # Create IV chart
        greeks_chart = Chart("Implied Volatility")
        for strike in self.target_strikes:
            greeks_chart.add_series(Series(f"Call IV {strike}", SeriesType.LINE, "%"))
            greeks_chart.add_series(Series(f"Put IV {strike}", SeriesType.LINE, "%"))
        self.add_chart(greeks_chart)
        
        # Create options price chart
        prices_chart = Chart("Option Prices")
        for strike in self.target_strikes:
            prices_chart.add_series(Series(f"Call Price {strike}", SeriesType.LINE, "$"))
            prices_chart.add_series(Series(f"Put Price {strike}", SeriesType.LINE, "$"))
        self.add_chart(prices_chart)
    
    def on_data(self, slice):
        current_date = self.time.date()
        
        # If new day, plot previous day's averages and reset
        if self.current_date is not None and self.current_date != current_date:
            self.plot_daily_averages()
            self.daily_data = {}
        
        self.current_date = current_date
        
        if self.option_symbol not in slice.option_chains:
            return
        
        chain = slice.option_chains[self.option_symbol]
        if len(chain) == 0:
            return
        
        calls = [c for c in chain if c.right == OptionRight.CALL
                 and abs((c.expiry.date() - self.target_date).days) < 7
                 and c.strike in self.target_strikes]
        puts = [c for c in chain if c.right == OptionRight.PUT
                and abs((c.expiry.date() - self.target_date).days) < 7
                and c.strike in self.target_strikes]
        
        # Accumulate data for each strike
        for call in calls:
            if call.strike not in self.daily_data:
                self.daily_data[call.strike] = {'call_ivs': [], 'put_ivs': [], 'call_prices': [], 'put_prices': []}
            self.daily_data[call.strike]['call_ivs'].append(call.implied_volatility * 100)
            self.daily_data[call.strike]['call_prices'].append(call.last_price)
        
        for put in puts:
            if put.strike not in self.daily_data:
                self.daily_data[put.strike] = {'call_ivs': [], 'put_ivs': [], 'call_prices': [], 'put_prices': []}
            self.daily_data[put.strike]['put_ivs'].append(put.implied_volatility * 100)
            self.daily_data[put.strike]['put_prices'].append(put.last_price)
    
    def plot_daily_averages(self):
        """Plot the average IV and prices for each strike for the day"""
        for strike, data in self.daily_data.items():
            if len(data['call_ivs']) > 0:
                avg_call_iv = sum(data['call_ivs']) / len(data['call_ivs'])
                self.plot("Implied Volatility", f"Call IV {strike}", avg_call_iv)
            
            if len(data['put_ivs']) > 0:
                avg_put_iv = sum(data['put_ivs']) / len(data['put_ivs'])
                self.plot("Implied Volatility", f"Put IV {strike}", avg_put_iv)
            
            if len(data['call_prices']) > 0:
                avg_call_price = sum(data['call_prices']) / len(data['call_prices'])
                self.plot("Option Prices", f"Call Price {strike}", avg_call_price)
            
            if len(data['put_prices']) > 0:
                avg_put_price = sum(data['put_prices']) / len(data['put_prices'])
                self.plot("Option Prices", f"Put Price {strike}", avg_put_price)
    
    def on_end_of_algorithm(self):
        """Plot the last day's data when backtest ends"""
        self.plot_daily_averages()