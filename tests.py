# Testing suite for the application
import shutil
import os

import process
import helper


def test_history_read_0():
    """
    Test to handle graceful fail-over with no prior history file
    """

    # Setup
    helper.cleanup()

    # Actual application test
    viability_scores, aliases = process.read_history()

    assert(len(viability_scores.keys()) == 0)
    assert(len(aliases.keys()) == 0)


def test_history_read_1():
    """
    Test to handle improperly configured history file: empty file
    """

    # Setup
    helper.cleanup()
    shutil.copyfile(process.TESTING_DIRECTORY + '/empty_file', process.HISTORY_FILE)

    # Actual application test
    viability_scores, aliases = process.read_history()

    assert(len(viability_scores.keys()) == 0)
    assert(len(aliases.keys()) == 0)

    # Teardown
    os.remove(process.HISTORY_FILE)


def test_history_read_2():
    """
    Test to handle improperly configured history file: bad keyword
    """

    # Setup
    helper.cleanup()
    shutil.copyfile(process.TESTING_DIRECTORY + '/test_history_2', process.HISTORY_FILE)

    # Actual application test
    viability_scores, aliases = process.read_history()

    assert (len(viability_scores.keys()) == 0)
    assert (len(aliases.keys()) == 0)

    # Teardown
    os.remove(process.HISTORY_FILE)


def test_history_read_3():
    """
    Test to handle a properly configured history file
    """

    # Setup
    helper.cleanup()
    shutil.copyfile(process.TESTING_DIRECTORY + '/test_history_3', process.HISTORY_FILE)

    # Correct values
    actual_scores = {
        'NYSE: GM': (float(200), 20, '2017-04-11T08:42:37.315456'),
        'NASDAQ: TSLA': (float(100), 60, '2017-04-11T08:42:37.315556'),
        'NYSE: UAL': (float(300), 60, '2017-04-11T08:42:37.315656'),
        'NASDAQ: AMD': (float(-200), 100, '2017-04-11T08:42:37.315756')
    }

    actual_aliases = {
        'General Motors': 'NYSE: GM',
        'GM': 'NYSE: GM',
        'TSLA': 'NASDAQ: TSLA',
        'Tesla': 'NASDAQ: TSLA',
        'UAL': 'NYSE: UAL',
        'United': 'NYSE: UAL',
        'United Airlines': 'NYSE: UAL',
        'AMD': 'NASDAQ: AMD',
        'AyyMD': 'NASDAQ: AMD',
        'Advanced Micro Devices': 'NASDAQ: AMD',
    }

    # Actual application test
    viability_scores, aliases = process.read_history()

    assert(viability_scores == actual_scores)
    assert(aliases == actual_aliases)

    # Teardown
    os.remove(process.HISTORY_FILE)


def test_input_0():
    """
    Test with an empty input file, should simply log and exit with error code 1
    """

    # Setup
    helper.cleanup()

    file_path = process.TESTING_DIRECTORY + '/empty_file'
    assert(helper.run_processing_engine(file_path) == 1)

    # Teardown
    helper.cleanup()


def test_input_1():
    """
    Test with a valid input file:
        - Single tweet
        - Single company (Tesla)
        - Positive sentiment
        - History file: base
    """

    # Setup
    helper.cleanup()
    shutil.copyfile(process.TESTING_DIRECTORY + '/base_aliases', process.HISTORY_FILE)

    file_path = process.TESTING_DIRECTORY + '/test_input_1'
    assert (helper.run_processing_engine(file_path) == 0)

    # Teardown
    helper.cleanup()


def test_input_2():
    """
    Test with a valid input file:
        - Single tweet
        - Single company (United Airlines)
        - Negative sentiment
        - History file: base
    """

    # Setup
    helper.cleanup()
    shutil.copyfile(process.TESTING_DIRECTORY + '/base_aliases', process.HISTORY_FILE)

    file_path = process.TESTING_DIRECTORY + '/test_input_2'
    assert (helper.run_processing_engine(file_path) == 0)

    # Teardown
    helper.cleanup()


def test_input_3():
    """
    Test with a valid input file:
        - 2 tweets, single company per tweet
        - Two companies (Tesla and GM)
        - Positive sentiment for Tesla
        - Negative sentiment for GM
        - History file: 3
    """

    # Setup
    helper.cleanup()
    shutil.copyfile(process.TESTING_DIRECTORY + '/base_aliases', process.HISTORY_FILE)

    file_path = process.TESTING_DIRECTORY + '/test_input_3'
    assert (helper.run_processing_engine(file_path) == 0)

    # Teardown
    helper.cleanup()


def test_input_4():
    """
    Test with a valid input file:
        - Single tweet
        - 2 companies (AMD and GM)
        - Negative sentiment
        - History file: base
    """

    # Setup
    helper.cleanup()
    shutil.copyfile(process.TESTING_DIRECTORY + '/test_history_3', process.HISTORY_FILE)

    file_path = process.TESTING_DIRECTORY + '/test_input_4'
    assert (helper.run_processing_engine(file_path) == 0)

    # Teardown
    helper.cleanup()


def test_input_5():
    """
    Test with a valid input file:
        - Single tweet
        - 2 companies (GM and Tesla)
        - Positive sentiment
        - History file: base
    """

    # Setup
    helper.cleanup()
    shutil.copyfile(process.TESTING_DIRECTORY + '/base_aliases', process.HISTORY_FILE)

    file_path = process.TESTING_DIRECTORY + '/test_input_5'
    assert (helper.run_processing_engine(file_path) == 0)

    # Teardown
    helper.cleanup()
