from typing import Dict, List, Optional, Tuple, Union

from .coingecko import *


def get_markdown_table(ranked: List[Tuple[str, int]],
                       cg_coins_list: Optional[List[Union[CoinMarket, Dict]]], top: int = 100) -> str:
    """
    Return a markdown table of the given list of ranked crypto mentions.
    """
    cg_coins_list = cg_coins_list or get_cg_coins_list()
    lines = []
    lines.append("Nr. | Count | Name | Ticker | Market Cap (USD) | Link")
    lines.append(":--- |----:|:----|:------:|--------------:|:----")
    for rank, (ticker, count) in enumerate(ranked):
        if rank > top - 1:
            break
        coin: CoinMarket = get_most_popular_coin_with_ticker(ticker, cg_coins_list)
        if not coin:
            print("No coin found for ticker:", ticker)
        else:
            lines.append(
                f"{rank + 1}. | {count} | {coin['name']} | {ticker.upper()} | ${coin['market_cap']:,} | [CoinGecko ↗](https://www.coingecko.com/en/coins/{coin['id']})")
    return "\n".join(lines)
