from typing import Any, Dict, List, Optional, TypedDict, Union

from pycoingecko import CoinGeckoAPI

cg = CoinGeckoAPI()


class CoinMarket(TypedDict):
    id: str
    name: str
    image: str
    current_price: float
    market_cap: int
    market_cap_rank: int
    fully_diluted_valuation: int
    total_volume: int
    high_24h: float
    low_24h: float
    price_change_24h: float
    price_change_percentage_24h: float
    market_cap_change_24h: int
    market_cap_change_percentage_24h: float
    circulating_supply: float
    total_supply: float
    max_supply: float
    ath: float
    ath_change_percentage: float
    ath_date: str
    atl: float
    atl_change_percentage: float
    atl_date: str
    roi: Any
    last_updated: str


def get_cg_coins_markets(vs_currency: str = "usd", limit: int = 1000) -> List[CoinMarket]:
    coins = []
    page = 1
    while len(coins) < limit:
        res = cg.get_coins_markets(vs_currency, per_page=250)
        if len(res) == 0:
            break
        for coin in res:
            coins.append(CoinMarket(**coin))
        page += 1

    return coins


def get_cg_coins_list():
    return cg.get_coins_list()


def get_symbols_names_dict(cg_coins_list: Optional[List[Union[CoinMarket, Dict]]]):
    cg_coins_list = cg_coins_list or get_cg_coins_list()
    cg_dict = {}
    for coin in cg_coins_list:
        if coin["symbol"].lower() in cg_dict:
            continue
        cg_dict[coin["symbol"].lower()] = coin["name"].lower()
    return cg_dict


def get_most_popular_coin_with_ticker(
        ticker: str, cg_coins_list: Optional[List[Union[CoinMarket, Dict]]]) -> Optional[Union[CoinMarket, Dict]]:
    cg_coins_list = cg_coins_list or get_cg_coins_list()
    coin: Union[CoinMarket, Dict] = None
    for c in cg_coins_list:
        if ticker.lower() == c["symbol"].lower():
            if coin:
                if "Binance-Peg" in coin["name"]:
                    coin = c
                if "market_cap" in coin and "market_cap" in c:
                    if coin["market_cap"] < c["market_cap"]:
                        coin = c
            else:
                coin = c
    return coin
