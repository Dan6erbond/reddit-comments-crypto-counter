# Reddit Comments Crypto Ticker Counter

A Python library, CLI tool, and Reddit bot that count the occurrences of cryptocoin mentions in Reddit threads.

## Usage

Clone the GitHub repository:

```sh
$ git clone https://github.com/Dan6erbond/reddit-comments-crypto-counter.git
```

Install the dependencies:

```sh
$ pip3 install -r requirements.txt
```

Create a `praw.ini` file as per the instructions from PRAW's [documentation](https://praw.readthedocs.io/en/stable/getting_started/configuration/prawini.html):

```ini
[CCC]
username=username
password=password
client_id=client_id
client_secret=client_secret
```

You can create a Reddit application [here](https://www.reddit.com/prefs/apps). Make sure it is a `script` type and the redirect URI is set to https://127.0.0.1/ or https://localhost/.

Run the command:

```sh
$ python3 main.py --top=100 --url=https://www.reddit.com/r/CryptoCurrency/comments/q3mxnq/as_of_today_what_are_your_top_5_longterm_crypto/ --no-ignore-english-words
```

## Arguments

```
--top
    The number of top crypto tickers to list.
    Default: 100

--url
    The URL of the Reddit submission to scan for comments in.
    Default: https://www.reddit.com/r/CryptoCurrency/comments/q3mxnq/as_of_today_what_are_your_top_5_longterm_crypto/

--ignore-english-words
    Ignore tickers that are common English words.
    Default: True

--no-ignore-english-words
    Do not ignore tickers that are common English words.
    Default: False
```

## Reddit Bot

The Reddit bot is found under the `bot` directory, and runs as the [/u/Crypto-Counter](https://www.reddit.com/u/Crypto-Counter) user. It can be summoned, using its username, or by including the `!CryptoMentions`, or `!CryptoCounter` command in a comment.

Additional call methods will be implemented in the future. Such as automatic detection of suitable threads to scan.

The bot will scan all the comments in a thread, and count the number of unique mentions of a cryptocoin in each comment. The results will be tallied and then displayed to comment, of which only one unique comment can exist per thread.

Should the bot be summoned multiple times in the same thread, it will respond with a link to the comment containing the rankings.

The bot will periodically update the rankings, and adjust its loop-time according to how old a submission is. This is in order to avoid overloading the host machine and Reddit's API, and to avoid unnecessary API calls.

## Contributors

- [Dan6erbond](https://github.com/Dan6erbond)

## License

[MIT.](./LICENSE)
