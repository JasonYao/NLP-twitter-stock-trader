import logging
from subprocess import Popen, PIPE
import signal
import os
import time

import re
import tweepy
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
from tweepy import Stream

import secrets

import time
from datetime import datetime


# Grabs non-application specific helper modules
import helper

"""
Front-end ingestion engine that'll
batch together input stream while
the backend processing is working
"""

INPUT_FILE = '.input'
POLLING_TIMEOUT = 10
USERS = [
    "1364930179",   # Warren Buffett
    "25073877",     # Donald Trump
    "133056605",    # Ultimate Stock Alerts
    "14886375",     # StockTwits
    "624413",       # MarketWatch
    "2837841",      # CNNMoneyInvest
    "16228398",     # Mark Cuban
    "50393960",     # Bill Gates
    "21323268",     # NYSE
    "184020744",    # Mike Flache
    "19546277",     # YahooFinance
    "778670441405775872", # MarketsInsider
    ]

KEYWORDS = [
        "NYSE",
        "IPO",
        "NASDAQ",
]

NEXT_TWEET_BATCH = []


class Tweet:
    def __init__(self, text, retweets, favorites, time):
        self.tweet_text = text
        self.retweet_count = retweets
        self.favorite_count = favorites
        self.timestamp = time

    def __str__(self):
        # tweet text|retweets+fav|timestamp
        return self.tweet_text + "|" + str(self.retweet_count + self.favorite_count) + "|" \
               + str(datetime.strptime(str(self.timestamp), '%Y-%m-%d %H:%M:%S'))


class SListener(StreamListener):

    def on_status(self, status):
        if (len(NEXT_TWEET_BATCH) < 100):
            # if status.user.id_str in USERS:
            # if not status.retweeted and ('RT @' not in status.text):
            print(status.favorite_count)
            print(status.retweet_count)
            print(status.user.screen_name)
            print(status.text)
            print(status.created_at)
            print(len(NEXT_TWEET_BATCH))
            status.text = status.text.replace('\n', '')
            status.text = status.text.replace('|', '')
            new_tweet = Tweet(status.text, status.retweet_count, status.favorite_count, status.created_at)
            NEXT_TWEET_BATCH.append(new_tweet)
            return True
        else:
            return False


    def on_error(self, status_code):
        if status_code == 420:
            # Disconnect the stream
            return False


def generate_input_file():
    global NEXT_TWEET_BATCH
    logging.info("Writing tweets to input file")
    with open(INPUT_FILE, "w") as input_file:
        for tweet in NEXT_TWEET_BATCH:
            input_file.write(str(tweet) + "\n")
    logging.info("Input file successfully generated")
    NEXT_TWEET_BATCH = []


def handler(signum, frame):
    print("\nChecking if processing engine is done with the last batch")
    raise ValueError()


def main():
    # Initial setup
    args = helper.parse_args()
    helper.setup_logging(args.verbose)
    logging.info("Polling is set to: " + str(int(POLLING_TIMEOUT)) + " seconds")

    # Make call to twitter's streaming API to gather tweets
    while True:
        print('Gathering tweets from twitter\n')
        try:
            try:
                auth = OAuthHandler(secrets.consumer_key, secrets.consumer_secret)
                auth.set_access_token(secrets.access_token, secrets.access_token_secret)
                twitter_stream = tweepy.Stream(auth, SListener())
                twitter_stream.filter(follow=USERS)
            except:
                print("Authentication error")
                twitter_stream.disconnect()

            # Writes the processing input file
            generate_input_file()

            # Starts the background process
            background_process = Popen(["python", "process.py", INPUT_FILE], stdout=PIPE)

            while background_process.poll() is None:
                print("[SA engine]\t\tStatus: Currently processing a batch.")

                # Signal handling
                signal.signal(signal.SIGALRM, handler)
                signal.alarm(POLLING_TIMEOUT)

                try:
                    auth = OAuthHandler(secrets.consumer_key, secrets.consumer_secret)
                    auth.set_access_token(secrets.access_token, secrets.access_token_secret)
                    twitter_stream = tweepy.Stream(auth, SListener())
                    twitter_stream.filter(follow=USERS)
                except ValueError:
                    print("Checking if backend if free for the next batch")
                except:
                    print("Authentication error")
                    twitter_stream.disconnect()

            # At this point, the last batch is complete
            print("The last batch is now complete, processing next batch.")
            print("--------------------")
        except KeyboardInterrupt:
            print("\nCleaning up and exiting the ingestion engine")
            if os.path.isfile(INPUT_FILE):
                os.remove(INPUT_FILE)
            break


if __name__ == '__main__':
    main()
