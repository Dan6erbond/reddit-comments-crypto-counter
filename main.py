import argparse

import praw
from praw.reddit import Submission

from coingecko import *
from reddit_comments_crypto_counter import *
from formatting import *


def main(reddit: praw.Reddit, url: str, top: int = 100, markdown: bool = False):
    cg_coins_market = get_cg_coins_markets()
    submission: Submission = reddit.submission(url=url)
    ranked, comments_analyzed = analyze_comments(submission, cg_coins_market)
    if ranked:
        if markdown:
            print(get_markdown_table(ranked, cg_coins_market, top))
        else:
            for rank, (ticker, count) in enumerate(ranked):
                if rank > top - 1:
                    break
                coin: CoinMarket = get_most_popular_coin_with_ticker(ticker, cg_coins_market)
                if not coin:
                    print("No coin found for ticker:", ticker)
                else:
                    print(f"{rank + 1}. {coin['name']} ({ticker.upper()}) - {count} (Market Cap: ${coin['market_cap']:,})")
                    print()
    else:
        print("No coins found in thread.")
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
parser.add_argument("--markdown", "-md", dest="markdown", action="store_true",
                    default=False, help="Enable markdown output with CoinGecko URL.")

if __name__ == "__main__":
    args = parser.parse_args()
    reddit = praw.Reddit("CCC", user_agent="Reddit crypto comments ticker counter by Dan6erbond.")
    main(reddit, args.url, args.top, args.markdown)
