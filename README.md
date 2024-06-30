# Trading bot using FinBERT

## Conda environment setup

### Installing and activating

```bash
$ git clone https://github.com/the-phinisher/trading-bot.git
$ cd ./trading-bot
$ conda env create -f environment.yml
$ conda activate trader
```

> **Note**
> This creates conda environment named "trader". If one already exists, you have to rename one of them.

### Deactivating the environment

```bash
$ conda deactivate
```

## Setting environment variables
Go to [Alpaca's website](https://alpaca.markets), after logging in or creating an account, you can generate new API credentials.

> **Warning** Make sure you do not share your API credentials.

```bash
$ export BASE_URL="<BASE_URL>"
$ export API_KEY="<API_KEY>"
$ export API_SECRET="<API_SECRET>"
```

## Running

```bash
$ python tradingbot.py
```
