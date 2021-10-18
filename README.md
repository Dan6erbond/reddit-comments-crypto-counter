# Reddit Comments Crypto Ticker Counter

A simple Python CLI tool to count the occurrences of crypto tickers in Reddit comment threads.

## Usage

Clone the GitHub repository:

```sh
$ git clone https://github.com/Dan6erbond/reddit-comments-crypto-counter.git
```

Install the dependencies:

```sh
$ pip3 install -r requirements.txt
```

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

## Contributors

- [Dan6erbond](https://github.com/Dan6erbond)

## License

[MIT.](./LICENSE)
