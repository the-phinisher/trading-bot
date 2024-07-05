from lumibot.brokers import Alpaca
from lumibot.backtesting import YahooDataBacktesting
from lumibot.strategies.strategy import Strategy
from lumibot.traders import Trader
from alpaca_trade_api import REST
from timedelta import Timedelta
from finbert_utils import estimate_sentiment

class MLTrader(Strategy):
    def initialize(self, creds: dict, symbol: str = "SPY", cash_at_risk: float = 0.5):
        self.symbol = symbol
        self.sleeptime = "24H"
        self.last_trade = None
        self.cash_at_risk = cash_at_risk
        self.api = REST(base_url=creds["BASE_URL"], key_id=creds["API_KEY"], secret_key=creds["API_SECRET"])

    def position_sizing(self):
        cash = self.get_cash()
        last_price = self.get_last_price(self.symbol)
        quantity = int(cash * self.cash_at_risk / last_price)
        return cash, last_price, quantity

    def get_dates(self):
        today = self.get_datetime()
        three_days_prior = today - Timedelta(days=3)
        return today.strftime("%Y-%m-%d"), three_days_prior.strftime("%Y-%m-%d")

    def get_sentiment(self):
        today, three_days_prior = self.get_dates()
        news = self.api.get_news(symbol=self.symbol, start=three_days_prior, end=today)
        news = [ev.__dict__["_raw"]["headline"] for ev in news]
        probability, sentiment = estimate_sentiment(news)
        return probability, sentiment

    def on_trading_iteration(self):
        cash, last_price, quantity = self.position_sizing()
        probability, sentiment = self.get_sentiment()

        if cash > last_price:
            if sentiment == "positive" and probability > 0.9:
                if self.last_trade == "sell":
                    self.sell_all()
                order = self.create_order(
                    self.symbol,
                    quantity,
                    "buy",
                    type="bracket",
                    take_profit_price=last_price * 1.20,
                    stop_loss_price=last_price * 0.95,
                )
                self.submit_order(order)
                self.last_trade = "buy"
            elif sentiment == "negative" and probability > 0.9:
                if self.last_trade == "buy":
                    self.sell_all()
                order = self.create_order(
                    self.symbol,
                    quantity,
                    "sell",
                    type="bracket",
                    take_profit_price=last_price * 0.8,
                    stop_loss_price=last_price * 1.05,
                )
                self.submit_order(order)
                self.last_trade = "sell"

if __name__ == "__main__":
    import os
    import argparse
    from datetime import datetime

    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("-b", "--backtest", action='store_true')
    argument_parser.add_argument("-d", "--deploy", action='store_true')
    args = argument_parser.parse_args()

    API_KEY = os.environ["API_KEY"]
    API_SECRET = os.environ["API_SECRET"]
    BASE_URL = os.environ["BASE_URL"]

    ALPACA_CREDS = {"API_KEY": API_KEY, "API_SECRET": API_SECRET, "PAPER": True, "BASE_URL": BASE_URL}
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2024, 6, 13)
    broker = Alpaca(ALPACA_CREDS)
    strategy = MLTrader(
        name="mlstrat", broker=broker, parameters={"creds": ALPACA_CREDS, "symbol": "SPY", "cash_at_risk": 0.5}
    )
    if args.backtest:
        strategy.backtest(
            YahooDataBacktesting,
            start_date,
            end_date,
            parameters={"creds": ALPACA_CREDS, "symbol": "SPY", "cash_at_risk": 0.5},
        )

    if args.deploy:
        trader = Trader()
        trader.add_strategy(strategy)
        trader.run_all()