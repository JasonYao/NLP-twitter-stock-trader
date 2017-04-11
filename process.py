# Application imports
import logging
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
HISTORY_FILE = '.app.history'
TRADE_FILE = '.app.trades'

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
                'score' => The line contains a company name, its current viability score,
                    the current weight, and its timestamp as a tuple
                'alias' => The line contains a company's name and their stock ticker tuple
            """
            history_reader = csv.reader(history, skipinitialspace=True)
            for line in history_reader:
                indicator = line[0]
                if indicator == 'score':
                    viability_scores[line[1]] = (float(line[2]), int(line[3]), line[4])
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


def extract_companies(message_tokens, aliases):
    extracted_companies = []
    for token in message_tokens:
        if token in aliases:
            extracted_companies.append(token)

    return extracted_companies


def get_log_probability(token):
    #TODO implement
    return 5


def get_sentiment_analysis(tweet, aliases):
    """
    Given a tweet which is a tuple, where:
        tweet[0] -> Tweet message
        tweet[1] -> Tweet weight, how important/wide-spread this tweet is
        tweet[2] -> Tweet timestamp, when the tweet was given

    This function will extract any companies
    from it, and returns the sentiment scores
    for each company mentioned.

    White paper basis for this analysis is located at:
    http://cs229.stanford.edu/proj2011/ChenLazer-SentimentAnalysisOfTwitterFeedsForThePredictionOfStockMarketMovement.pdf
    """
    new_companies = {}
    message = tweet[0]
    weight = float(tweet[1])
    timestamp = tweet[2]

    # Tokenises the tweet into words
    tokens = message.split()

    # TODO actual NLP shit here
    # Extracts any company names
    extracted_companies = set(extract_companies(tokens, aliases))

    # Sanity check in case no company's name could be found in the tweet
    if len(extracted_companies) == 0:
        return new_companies

    log_probability = 0.0

    # For each word token, look up log-probability
    # in Alex Davies' word list, ignore if it is not found
    for token in tokens:
        # Sum all log probabilities for the 'bullish'
        # or 'bearish' sentiment of the entire tweet
        log_probability += get_log_probability(token)

    for company in extracted_companies:
        new_companies[company] = (log_probability, weight/10, timestamp)

    return new_companies


def add_new_state(viability_scores, new_companies):
    """
    Adds a list of new companies to the current list
        new_companies[company name][0] = score
        new_companies[company name][1] = weight
        new_companies[company name][2] = timestamp
    """
    for new_company, company_information in new_companies.items():
        new_score = company_information[0]
        new_weight = company_information[1]
        new_timestamp = company_information[2]

        if new_company in viability_scores:
            # There already exists a base score, updates it with the new information
            new_weight = viability_scores[new_company][1] + new_weight
            new_score = (viability_scores[new_company][0] + new_score) / new_weight
            # TODO don't just replace with the next timestamp, find actual latest one by time
            viability_scores[new_company] = (new_score, new_weight, new_timestamp)
        else:
            # There does not exist a base score, in which case one is generated, and the new information added to it
            viability_scores[new_company] = ((2000.0 + new_score) / 2, 1 + new_weight, new_timestamp)
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
                tweet = line.split('|')

                # Strips out newline if it has one at the end
                tweet[-1] = tweet[-1].strip()

                new_companies = get_sentiment_analysis(tweet, aliases)
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
        for company, company_information in viability_scores.items():
            logging.info(company_information)
            score = company_information[0]
            weight = company_information[1]
            timestamp = company_information[2]
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
            history_file.write('score, ' + company + ', ' + str(score[0]) + ', ' + str(score[1]) + '\n')

        # Prints out any aliases gathered
        for company, ticker in aliases.items():
            history_file.write('alias, ' + company + ', ' + ticker + '\n')


def main():
    args, file_name = helper.parse_args()

    # Initial setup
    helper.setup_logging(args.verbose)
    logging.info("Logging is now setup")

    # Gets prior history if available, clean state if not
    logging.info('-------------------- READING HISTORY END --------------------')
    viability_scores, aliases = read_history()

    # Debugging
    helper.log_state('history read-in', viability_scores, aliases)
    logging.info('-------------------- READING HISTORY END --------------------')

    # Gets the current ingestion batch from an input file
    logging.info('-------------------- INPUT FILE START --------------------')
    viability_scores, aliases = parse_input(viability_scores, aliases, file_name)

    # Debugging
    helper.log_state('input file read-in', viability_scores, aliases)
    logging.info('-------------------- INPUT FILE END --------------------')

    # Writes any trades to disk
    write_trades(viability_scores)

    # Writes the SA state to history
    write_history(viability_scores, aliases)


if __name__ == '__main__':
    main()
