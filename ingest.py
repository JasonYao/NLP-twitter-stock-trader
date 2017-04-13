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
    "1364930179", # Warren Buffet
    "25073877", # Donald Trump
]

class SListener(StreamListener):

    def on_data(self, data):
        print (data)
        print('inside of in_data')
        return True

    def on_status(self, status):
        print('inside of on_status')
        print(status.text)

    def on_error(self, status_code):
        if status_code == 420:
            # returning False in on_data disconnects the stream
            return False


def generate_input_file(tweets):
    logging.info("Writing tweets to input file")
    with open(INPUT_FILE, "w") as input_file:
        for tweet in tweets:
            input_file.write(tweet)
    logging.info("Input file successfully generated")


def handler(signum, frame):
    print("\nChecking if processing engine is done with the last batch")
    raise ValueError()


def main():
    # Initial setup
    args = helper.parse_args()
    helper.setup_logging(args.verbose)
    logging.info("Polling is set to: " + str(int(POLLING_TIMEOUT)) + " seconds")

    # Batches input while waiting for last batch to finish
    next_tweet_batch = []

    print('Gathering tweets from twitter\n')
    # TODO make a call to twitter's streaming or RESTful API to gather tweets
    auth = OAuthHandler(secrets.consumer_key, secrets.consumer_secret)
    print("authenicated")
    auth.set_access_token(secrets.access_token, secrets.access_token_secret)
    print("2")
    twitter_stream = tweepy.Stream(auth, SListener())
    print("3")

    try:
        print("here")
        twitter_stream.filter(track=["twitter"])
    except:
        print "error!"
        twitter_stream.disconnect()

    print("filtered")

    # while True:
    #     print('Gathering tweets from twitter\n')
    #     # TODO make a call to twitter's streaming or RESTful API to gather tweets
    #     auth = OAuthHandler(secrets.consumer_key, secrets.consumer_secret)
    #     auth.set_access_token(secrets.access_token, secrets.access_token_secret)
    #     twitter_stream = Stream(auth, StreamListener())
    #     twitter_stream.filter(track="united")


        # # Starts the background process
        # background_process = Popen(["python", "process.py", INPUT_FILE], stdout=PIPE)
        # background_trade = Popen(["python", "trade.py"], stdout=PIPE)
        #
        # # Polls the engines for their status
        # while True:
        #     # Deals with the SA processing engine
        #     if background_process.poll() is None:
        #         print("[SA engine]\t\tStatus: Currently processing a batch.")
        #     else:
        #         print("[SA engine]\t\tStatus: Done processing a batch, loading next tweet batch in.")
        #         # TODO make a new background process
        #         break
        #
        #     # Deals with the trading engine
        #     if background_trade.poll() is None:
        #         print("[Trading engine]\tStatus: Currently processing a batch.")
        #     else:
        #         print("[Trading engine]\tStatus: Done processing a batch. Checking for different SA output")
        #         # TODO make a new background trade if SA is not different
        #         break
        #
        #     # Signal handling
        #     signal.signal(signal.SIGALRM, handler)
        #     signal.alarm(POLLING_TIMEOUT)
        #
        #     try:
        #         time.sleep(3)
        #     except KeyboardInterrupt:
        #         print("\nCleaning up and exiting ingestion engine")
        #         if os.path.isfile(INPUT_FILE):
        #             os.remove(INPUT_FILE)
        #         exit(0)
        #     except ValueError:
        #         print("\nChecking if backend is free for the next batch")

        # At this point, the last batch is complete
        # print("The last batch is now complete, processing next batch.")
        # print("--------------------")


if __name__ == '__main__':
    main()
