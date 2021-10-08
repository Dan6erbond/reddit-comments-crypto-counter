import re
from typing import List, Union

import praw
from praw.models.comment_forest import CommentForest
from praw.models.reddit.more import MoreComments
from praw.reddit import Comment, Submission
from pycoingecko import CoinGeckoAPI

cg = CoinGeckoAPI()
cg_coins_list = cg.get_coins_list()
cg_dict = {}
for coin in cg_coins_list:
    if coin["symbol"].lower() in cg_dict:
        continue
    cg_dict[coin["symbol"].lower()] = coin["name"].lower()

reddit = praw.Reddit("CCC", user_agent="Reddit crypto comments ticker counter by Dan6erbond.")

post: Submission = reddit.submission(
    url="https://www.reddit.com/r/CryptoCurrency/comments/q3mxnq/as_of_today_what_are_your_top_5_longterm_crypto/")

comments: List[Union[Comment, MoreComments]] = post.comments.list()

ticker_re = re.compile(r"\b([a-zA-Z]{3,5})\b")

cryptos = {}
comments_analyzed = 0

while comments:
    cs = [*comments]
    comments = []
    for comment in cs:
        if isinstance(comment, Comment):
            comments_analyzed += 1
            for match in ticker_re.finditer(comment.body):
                ticker = match.group(1).lower()
                if ticker in cg_dict:
                    if ticker in cryptos:
                        cryptos[ticker] += 1
                    else:
                        cryptos[ticker] = 1
            for symbol, name in cg_dict.items():
                if name in comment.body.lower():
                    if symbol in cryptos:
                        cryptos[symbol] += 1
                    else:
                        cryptos[symbol] = 1
        else:
            forest: CommentForest = comment.comments()
            forest.replace_more()
            comments.extend(forest.list())

ranked = sorted(cryptos.items(), key=lambda x: x[1], reverse=True)
for rank, (ticker, count) in enumerate(ranked):
    if rank > 99:
        break
    name = ""
    for coin in cg_coins_list:
        if ticker.lower() == coin["symbol"].lower():
            name = coin["name"]
            break
    print(f"{rank + 1}. {name} ({ticker.upper()}) - {count}")
    print()
print(f"{comments_analyzed} comments analyzed.")
