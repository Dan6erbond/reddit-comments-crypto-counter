import argparse

from coingecko import *
from reddit_comments_crypto_counter import *


def main(url: str, top: int = 100):
    cg_coins_list = get_cg_coins_list()
    ranked, comments_analyzed = analyze_comments(url, cg_coins_list)
    for rank, (ticker, count) in enumerate(ranked):
        if rank > top - 1:
            break
        name = ""
        for coin in cg_coins_list:
            if ticker.lower() == coin["symbol"].lower():
                name = coin["name"]
        print(f"{rank + 1}. {name} ({ticker.upper()}) - {count}")
        print()
    print(f"{comments_analyzed:,} comments analyzed.")


parser = argparse.ArgumentParser(description="Scan Reddit comment trees for crypto coin tickers and names.")
parser.add_argument("--top", dest="top", type=int, default=100, help="Number of top cryptocurrencies to show.")
parser.add_argument(
    "--url",
    dest="url",
    type=str,
    default="https://www.reddit.com/r/CryptoCurrency/comments/q3mxnq/as_of_today_what_are_your_top_5_longterm_crypto/",
    help="URL of the Reddit submission to analyze.")
parser.add_argument("--ignore-english-words", dest="ignore_english_words", action="store_true",
                    default=True, help="Ignore English words in comments that may be detected as coins or tokens.")
parser.add_argument("--no-ignore-english-words", dest="ignore_english_words", action="store_false")

if __name__ == "__main__":
    args = parser.parse_args()
    main(args.url, args.top)
