from typing import Dict, List

from pycoingecko import CoinGeckoAPI

cg = CoinGeckoAPI()


def get_cg_coins_list():
    return cg.get_coins_list()


def get_symbols_names_dict(cg_coins_list: List[Dict]):
    cg_coins_list = cg_coins_list or get_cg_coins_list()
    cg_dict = {}
    for coin in cg_coins_list:
        if coin["symbol"].lower() in cg_dict:
            continue
        cg_dict[coin["symbol"].lower()] = coin["name"].lower()
    return cg_dict
