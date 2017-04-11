# Application imports
import logging
import time
import csv

# Grabs non-application specific helper modules
import helper

"""
Back-end processing engine that'll
process a given batch of tweets
"""


# Global files & directories
LOGGING_DIRECTORY = 'logs'
TESTING_DIRECTORY = 'tests'
HISTORY_FILE = 'app.history'
TRADE_FILE = 'app.trades'

# Global constants
CALL_THRESHOLD_SOFT = 2200
CALL_THRESHOLD_HARD = 2400

PUT_THRESHOLD_SOFT = 1800
PUT_THRESHOLD_HARD = 1600


def read_history():
    """
    Reads prior history in if available,
    returns either current state from history
    or clean initial state if there are errors/no history
    """

    # Empty initial values in case of no history
    viability_scores = {}
    aliases = {}

    try:
        # Sanity check: empty file
        if helper.is_empty_file(HISTORY_FILE):
            raise ValueError()

        with open(HISTORY_FILE, "r") as history:
            """
            The first word in the history is an indicator:
                'score' => The line contains a company name and current viability score tuple
                'alias' => The line contains a company's name and their stock ticker tuple
            """
            history_reader = csv.reader(history, skipinitialspace=True)
            for line in history_reader:
                indicator = line[0]
                if indicator == 'score':
                    viability_scores[line[1]] = float(line[2])
                elif indicator == 'alias':
                    aliases[line[1]] = line[2]
                else:
                    raise ValueError()
            logging.info("History has now been read successfully")
    except (IndexError, IOError, ValueError):
        # In case history file was invalid part way through, we reset it all
        logging.info("History file not found, defaulting to clean state")
        viability_scores = {}
        aliases = {}

    return viability_scores, aliases


def get_sentiment_analysis(line, aliases):
    """
    Given a line that contains a tweet, extracts any
    companies from it and returns the sentiment scores
    for each.
    """
    new_companies = {}

    # TODO actual NLP shit here

    return new_companies


def add_new_state(viability_scores, new_companies):
    for new_company, new_score in new_companies.items():
        if new_company in viability_scores:
            # There already exists a base score, updates it with the new information
            viability_scores[new_company] = viability_scores[new_company] + new_companies[new_company]
        else:
            # There does not exist a base score, in which case one is generated, and the new information added to it
            viability_scores[new_company] = 2000 + new_companies[new_company]
    return viability_scores


def parse_input(viability_scores, aliases, input_file_name):
    """
    Given prior history/clean state, and an input file
    of new expressions, adds the new expressions to the
    current state, and returns the new state
    """
    try:
        # Sanity check: Empty file
        if helper.is_empty_file(input_file_name):
            raise ValueError()

        with open(input_file_name, "r") as input_file:
            for line in input_file:
                new_companies = get_sentiment_analysis(line, aliases)
                viability_scores = add_new_state(viability_scores, new_companies)
            logging.info("Input has now been read successfully")
    except (IOError, ValueError):
        logging.warning("Input file was either not found or was empty, exiting now")
        exit(1)

    return viability_scores, aliases


def write_trades(viability_scores):
    """
    Given a list of viability scores, writes
    a trade down if it is above/below a certain
    threshold
    """
    with open(TRADE_FILE, "w") as trade_file:
        for company, score in viability_scores.items():
            if CALL_THRESHOLD_SOFT <= score <= CALL_THRESHOLD_HARD:
                trade_file.write('call, ' + company + ', soft')
            elif score >= CALL_THRESHOLD_HARD:
                trade_file.write('call, ' + company + ', hard')
            elif PUT_THRESHOLD_SOFT >= score >= PUT_THRESHOLD_HARD:
                trade_file.write('put, ' + company + ', soft')
            elif score <= PUT_THRESHOLD_HARD:
                trade_file.write('put, ' + company + ', hard')
            else:
                logging.warning('Error: trading could not write for: ' + company + ' with a score of: ' + str(score))


def write_history(viability_scores, aliases):
    """
    The first word in the history is an indicator:
        'score' => The line contains a company name and current viability score tuple
        'alias' => The line contains a company's name and their stock ticker tuple
    """
    with open(HISTORY_FILE, "w") as history_file:
        # Prints out the companies and scores
        for company, score in viability_scores.items():
            history_file.write('score, ' + company + ', ' + str(score) + '\n')

        # Prints out any aliases gathered
        for company, ticker in aliases.items():
            history_file.write('alias, ' + company + ', ' + ticker + '\n')


def main():
    args, file_name = helper.parse_args()

    # Initial setup
    helper.setup_logging(args.verbose)

    # Gets prior history if available, clean state if not
    viability_scores, aliases = read_history()

    # Gets the current ingestion batch from an input file
    viability_scores, aliases = parse_input(viability_scores, aliases, file_name)

    # Writes any trades to disk
    write_trades(viability_scores)

    # Writes the SA state to history
    write_history(viability_scores, aliases)


if __name__ == '__main__':
    main()
