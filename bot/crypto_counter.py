import argparse
import logging
import sys
import threading
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Literal, Union, overload

import praw
from lib import *
from lib import analyze_comments as analyze_submission_comments
from lib.coingecko import *
from lib.formatting import get_markdown_table
from praw.reddit import Comment, Submission
from tinydb import Query, TinyDB
from tinydb.table import Document

reddit = praw.Reddit("CCC", user_agent="Reddit crypto comments ticker counter by /u/Dan6erbond.")
reddit.validate_on_submit = True
subreddits = reddit.multireddit("Dan6erbond", "crypto")

db = TinyDB("crypto_counter_bot.json")

logger = logging.getLogger("CryptoCounter")
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger.setLevel(logging.DEBUG)
logger.propagate = False

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(logging.WARN)
stream_handler.setFormatter(formatter)

logger.addHandler(stream_handler)

file_handler = logging.FileHandler("bot.txt", "a+", "utf-8")
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

cg_coins_market: List[CoinMarket] = None
cg_coins_market_last_updated: datetime = None

bot_disclaimer = """\n\n
 I am a bot built by /u/Dan6erbond.
 Results may not be accurate.
 Please report any issues on my [GitHub](https://github.com/Dan6erbond/reddit-comments-crypto-counter)."""

previous_submission_thread_started: datetime = None


class DocumentType(str, Enum):
    submission = "submission"
    comment = "comment"


def initialize_test():
    global db, subreddits
    db = TinyDB("crypto_counter_bot_test.json")
    subreddits = reddit.subreddit("test")


def get_submission(submission_id: str) -> Document:
    Submission = Query()
    res: List[Document] = db.search(
        (Submission.type == DocumentType.submission) & (
            Submission.id == submission_id))
    return res[0] if res else None


@overload
def create_submission(submission_id: str, return_submission: Literal[False]) -> int: ...
@overload
def create_submission(submission_id: str, return_submission: Literal[True]) -> Document: ...


def create_submission(submission_id: str, return_submission: bool = False) -> Union[int, Document]:
    doc_id = db.insert({
        "id": submission_id,
        "type": DocumentType.submission,
    })
    return db.get(doc_id=doc_id) if return_submission else doc_id


def analyze_submissions():
    for submission in subreddits.stream.submissions(skip_existing=True):
        submission: Submission
        # TODO: Check if submission is applicable for analysis
        start_submission_thread(submission)


def analyze_submission(submission: Submission, db_submission: Document, parent_comment: Comment = None):
    global cg_coins_market_last_updated, cg_coins_market

    while True:
        if submission.locked:
            logger.warn(f"Submission {submission.id} is locked, skipping...")
            db.update({"ignore": True}, doc_ids=[db_submission.doc_id])
            return
        if submission.subreddit.user_is_banned:
            logger.warn(
                f"Subreddit {submission.subreddit.display_name} is banned, skipping submission {submission.id}...")
            db.update({"ignore": True}, doc_ids=[db_submission.doc_id])
            return
        if submission.num_comments < 1:
            logger.warn(f"Submission {submission.id} has no comments, skipping...")
            return

        created = datetime.utcfromtimestamp(submission.created_utc)
        age = datetime.utcnow() - created

        if age > timedelta(weeks=2):
            logger.warn(
                f"Submission {submission.id} is too old to handle, skipping...")
            db.update({"ignore": True}, doc_ids=[db_submission.doc_id])
            return

        if age > timedelta(days=1):
            time_interval = 1 * 60 * 60
        elif age > timedelta(hours=4):
            time_interval = 30 * 60
        elif age > timedelta(hours=2):
            time_interval = 20 * 60
        elif age > timedelta(hours=1):
            time_interval = 10 * 60
        else:
            time_interval = 5 * 60

        try:
            if not cg_coins_market_last_updated or datetime.now() - cg_coins_market_last_updated > timedelta(hours=1):
                cg_coins_market = get_cg_coins_markets()
                cg_coins_market_last_updated = datetime.now()

            logger.info("Analyzing submission: " + submission.id)
            ranked, _ = analyze_submission_comments(submission, cg_coins_market)
            coin_mentions = sum(count for _, count in ranked)

            top = 75 if coin_mentions > 75 else 50 if coin_mentions > 50 else 25 if coin_mentions > 25 else 10 if coin_mentions > 10 else min(
                coin_mentions, 10)
            comment_text: str
            if ranked:
                comment_text = f"I've analyzed the submission! These were the top {top} crypto mentions:\n\n" + \
                    get_markdown_table(ranked, cg_coins_market, top) + \
                    f"\n\nLast updated: {datetime.now().strftime('%m/%d/%Y, %H:%M:%S')}" + bot_disclaimer
            else:
                comment_text = "I've analyzed the submission! Unfortunately, at the current time, no results were found." + \
                    f"\n\nLast updated: {datetime.now().strftime('%m/%d/%Y, %H:%M:%S')}" + bot_disclaimer
            if crypto_comments_id := db_submission.get("crypto_comments_id"):
                comment = reddit.comment(crypto_comments_id)
                comment.edit(comment_text)
            else:
                comment = submission.reply(comment_text) if not parent_comment else parent_comment.reply(comment_text)
                db.update({"crypto_comments_id": comment.id}, doc_ids=[db_submission.doc_id])
        except Exception as e:
            logger.error(str(e))
        finally:
            time.sleep(time_interval)


def start_submission_thread(submission: Submission, db_submission: Document = None, parent_comment: Comment = None):
    global previous_submission_thread_started
    if db_submission or (db_submission := get_submission(submission.id)):
        if crypto_comments_id := db_submission.get("crypto_comments_id"):
            if parent_comment:
                crypto_comment = reddit.comment(crypto_comments_id)
                parent_comment.reply(
                    "I've already analyzed this submission! " +
                    f"You can see the most updated results [here](https://reddit.com{crypto_comment.permalink}).")
            return
    else:
        db_submission = create_submission(submission.id, True)

    if previous_submission_thread_started and datetime.now() - previous_submission_thread_started < timedelta(seconds=10):
        time.sleep(10)  # Wait 10 seconds before starting another thread to avoid rate limiting

    threading.Thread(target=analyze_submission, args=(submission, db_submission, parent_comment)).start()
    previous_submission_thread_started = datetime.now()


def analyze_comments():
    for comment in subreddits.stream.comments(skip_existing=True):
        if any(mention.lower() in comment.body.lower()
               for mention in ["!CryptoMentions", "!CryptoCounter"]):
            start_submission_thread(comment.submission, parent_comment=comment)


def analyze_mentions():
    for mention in reddit.inbox.stream(skip_existing=True):
        if isinstance(mention, Comment):
            mention: Comment
            if f"u/{reddit.user.me().name.lower()}" in mention.body.lower():
                mention.mark_read()
                start_submission_thread(mention.submission, parent_comment=mention)


def analyze_database():
    Submission = Query()
    for doc in db.search((Submission.type == DocumentType.submission) & (Submission.ignore == False)):
        start_submission_thread(reddit.submission(doc["id"]), db_submission=doc)


def main():
    print("Starting Crypto Counter Bot...")
    logger.info("Starting database thread...")
    threading.Thread(target=analyze_database).start()
    logger.info("Starting comments thread...")
    threading.Thread(target=analyze_comments).start()
    logger.info("Starting inbox thread...")
    threading.Thread(target=analyze_mentions).start()
    # threading.Thread(target=analyze_submissions).start()


parser = argparse.ArgumentParser(description="Scan Reddit comment trees for crypto coin tickers and names.")
parser.add_argument("--test", "-t", dest="test", action="store_true", help="Run in test mode.")
parser.add_argument(
    "--clear-db",
    "-cdb",
    dest="clear_db",
    action="store_true",
    help="Clear the database.")
parser.set_defaults(test=False, clear_db=False)

if __name__ == "__main__":
    args = parser.parse_args()
    if args.test:
        print("Running in test mode.")
        initialize_test()
    if args.clear_db:
        print("Clearing DB.")
        db.truncate()
    main()
