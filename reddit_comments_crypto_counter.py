import re
from typing import List, Union

import praw
from english_words import english_words_lower_set
from praw.models.comment_forest import CommentForest
from praw.models.reddit.more import MoreComments
from praw.reddit import Comment, Submission

from coingecko import *

ticker_re = re.compile(r"\b([a-zA-Z]{2,5})\b")


def analyze_comments(reddit: praw.Reddit, url, cg_coins_list=None):
    cg_dict = get_symbols_names_dict(cg_coins_list)
    post: Submission = reddit.submission(url=url)
    comments: List[Union[Comment, MoreComments]] = post.comments.list()

    cryptos = {}
    comments_analyzed = 0

    while comments:
        cs = [*comments]
        comments = []
        for comment in cs:
            tickers = set()
            if isinstance(comment, Comment):
                comments_analyzed += 1
                for match in ticker_re.finditer(comment.body):
                    ticker = match.group(1)
                    ticker_lower = ticker.lower()
                    if ticker in english_words_lower_set and ticker.upper() != ticker:
                        continue
                    if ticker_lower in cg_dict and ticker_lower not in tickers:
                        if ticker_lower in cryptos:
                            cryptos[ticker_lower] += 1
                        else:
                            cryptos[ticker_lower] = 1
                        tickers.add(ticker_lower)
                for symbol, name in cg_dict.items():
                    if name in comment.body.lower() and symbol not in tickers:
                        if symbol in cryptos:
                            cryptos[symbol] += 1
                        else:
                            cryptos[symbol] = 1
                        tickers.add(symbol)
            else:
                forest: Union[CommentForest, List[Comment]] = comment.comments()
                if isinstance(forest, CommentForest):
                    forest.replace_more()
                    comments.extend(forest.list())
                else:
                    comments.extend(forest)

    ranked = sorted(cryptos.items(), key=lambda x: x[1], reverse=True)
    return ranked, comments_analyzed
