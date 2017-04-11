import logging
import datetime
import process
import argparse
import os

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


"""
Testing helper methods
"""


def cleanup():
    if os.path.isfile(process.HISTORY_FILE):
        os.remove(process.HISTORY_FILE)

    if os.path.isfile(process.TRADE_FILE):
        os.remove(process.TRADE_FILE)


def run_processing_engine(file_path):
    """
    Gives back the return code of running the processing engine given a file
    """
    from subprocess import Popen, PIPE
    p = Popen(["python", "process.py", file_path], stdout=PIPE)
    return p.wait()
