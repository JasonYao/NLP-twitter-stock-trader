import logging
import datetime
import process
import argparse
import os
import re
import string

"""
Application helper methods
"""


def is_empty_file(file_name):
    return os.stat(file_name).st_size == 0


def setup_logging(is_verbose):
    logging_file = process.LOGGING_DIRECTORY + '/' + datetime.datetime.now().isoformat() + '.log'
    if is_verbose:
        logging.basicConfig(filename=logging_file, level=logging.DEBUG)
    else:
        logging.basicConfig(filename=logging_file, level=logging.INFO)


def parse_args():
    parser = argparse.ArgumentParser(
        description='An application to utilise sentiment analysis to place stock trades'
    )

    parser.add_argument("-v", "--verbose", help="increase output verbosity",
                        action="store_true")

    args, file_name = parser.parse_known_args()

    if len(file_name) > 0:
        return args, file_name[0]
    else:
        return args


def log_state(initial_state, viability_scores, aliases):
    logging.debug('Viability scores after ' + initial_state + ':')
    for company, score in viability_scores.items():
        logging.debug('{0:<30} {1}'.format(company, str(score)))
    logging.debug('\n')

    logging.debug('Aliases after ' + initial_state + ':')
    for company, ticker in aliases.items():
        logging.debug('{0:<30} {1}'.format(company, ticker))
    logging.debug('\n')


def sanitise_tweet(some_string):
    """
    Removes links and special characters
    from a given string
    """
    return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])| (\w +: /  / \S +)", " ", some_string).split())


def strip_punctuation(some_string):
    """
    Removes punctuation from a given string
    """
    some_string = some_string.replace("'", " '")
    translator = str.maketrans('', '', string.punctuation)
    return some_string.translate(translator)


"""
Testing helper methods
"""


def cleanup():
    if os.path.isfile(process.HISTORY_FILE):
        os.remove(process.HISTORY_FILE)

    if os.path.isfile(process.TRADE_FILE):
        os.remove(process.TRADE_FILE)


def run_processing_engine(input_file):
    """
    Gives back the return code of running the processing engine given a file
    """
    from subprocess import Popen, PIPE
    p = Popen(["python", "process.py", input_file, "-v"], stdout=PIPE)
    return p.wait()
