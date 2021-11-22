import threading
import time
from datetime import datetime, timedelta

import praw
from praw.reddit import Submission

from coingecko import *
from reddit_comments_crypto_counter import *

reddit = praw.Reddit("CCC", user_agent="Reddit crypto comments ticker counter by Dan6erbond.")


def start_analyze(*args):
    time.sleep(60 * 15)
    while True:
        analyze_submission(*args)
        time.sleep(60 * 10)


def analyze_submission(submission: Submission, cg_coins_market: List[CoinMarket], top: int = 100):
    ranked, comments_analyzed = analyze_comments(submission, cg_coins_market)
    coin_mentions = sum(count for _, count in ranked)

    if comments_analyzed > 10 and coin_mentions >= 60 / 100 * comments_analyzed:
        print("Submission:", submission.title)
        print("URL:", f"https://reddit.com{submission.permalink}")
        print("Coin Mentions:", f"{coin_mentions:,}")
        print("Comments analyzed:", f"{comments_analyzed:,}")
        print("Percentage:", f"{coin_mentions / comments_analyzed * 100:.2f}%")
        print("\n")
        if ranked:
            for rank, (ticker, count) in enumerate(ranked):
                if rank > top - 1:
                    break
                coin: CoinMarket = get_most_popular_coin_with_ticker(ticker)
                if not coin:
                    print("No coin found for ticker:", ticker)
                else:
                    print(f"{rank + 1}. {coin['name']} ({ticker.upper()}) - {count} (Market Cap: ${coin['market_cap']:,})")
        else:
            print("No coins found in thread.")
        return True
    return False


def main():
    cg_coins_market = get_cg_coins_markets()
    cg_coins_market_last_updated = datetime.now()
    for submission in reddit.multireddit("Dan6erbond", "crypto").stream.submissions():
        submission: Submission

        if datetime.now() - cg_coins_market_last_updated > timedelta(hours=1):
            cg_coins_market = get_cg_coins_markets()
            cg_coins_market_last_updated = datetime.now()

        threading.Thread(target=start_analyze(submission, cg_coins_market)).start()


def test():
    cg_coins_market = get_cg_coins_markets()
    for submission in reddit.multireddit("Dan6erbond", "crypto").hot():
        submission: Submission
        try:
            if analyze_submission(submission, cg_coins_market):
                break
        except BaseException:
            continue


if __name__ == "__main__":
    test()
    # main()
