from AlgorithmImports import *
from datetime import datetime

class OptionsDataGraphAlgorithm(QCAlgorithm):
    def initialize(self):
        self.set_start_date(2024, 12, 1)
        self.set_end_date(2025, 2, 21)
        self.set_cash(100000)
        self.target_date = datetime(2025, 2, 21).date()
        self.target_strike = 230
        
        # Add AAPL options
        option = self.add_option("AAPL")
        self.option_symbol = option.symbol
        option.set_filter(-5, 5, 0, 90)
        
        # Track last plot date to ensure once-per-day plotting
        self.last_plot_date = None
        
        # Create only IV chart
        greeks_chart = Chart("Implied Volatility")
        greeks_chart.add_series(Series("Call IV", SeriesType.LINE, "%"))
        greeks_chart.add_series(Series("Put IV", SeriesType.LINE, "%"))
        self.add_chart(greeks_chart)

    def on_data(self, slice):
        # Only plot once per day
        current_date = self.time.date()
        if self.last_plot_date == current_date:
            return
        
        if self.option_symbol not in slice.option_chains:
            return
        
        chain = slice.option_chains[self.option_symbol]
        if len(chain) == 0:
            return
            
        calls = [c for c in chain if c.right == OptionRight.CALL
                and abs((c.expiry.date() - self.target_date).days) < 7
                and c.strike == self.target_strike]
        puts = [c for c in chain if c.right == OptionRight.PUT
                and abs((c.expiry.date() - self.target_date).days) < 7
                and c.strike == self.target_strike]
        
        if len(calls) > 0:
            # Plot only IV
            call = calls[0]
            self.plot("Implied Volatility", "Call IV", call.implied_volatility * 100)

        if len(puts) > 0:
            put = puts[0]
            self.plot("Implied Volatility", "Put IV", put.implied_volatility * 100)
            # Update last plot date
            self.last_plot_date = current_date            
