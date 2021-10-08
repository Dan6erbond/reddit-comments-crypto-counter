import re
from typing import List, Union

import praw
from english_words import english_words_lower_set
from praw.models.comment_forest import CommentForest
from praw.models.reddit.more import MoreComments
from praw.reddit import Comment, Submission

from coingecko import *

reddit = praw.Reddit("CCC", user_agent="Reddit crypto comments ticker counter by Dan6erbond.")
ticker_re = re.compile(r"\b([a-zA-Z]{3,5})\b")


def analyze_comments(url, cg_coins_list=None):
    cg_dict = get_symbols_names_dict(cg_coins_list)
    post: Submission = reddit.submission(url=url)
    comments: List[Union[Comment, MoreComments]] = post.comments.list()

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
                    if ticker in english_words_lower_set:
                        continue
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
    return ranked, comments_analyzed
