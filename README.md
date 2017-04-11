# Twitter Stock Trader (NLP Sentiment Analysis)
By [Jenna Denker](https://github.com/jndkr), [Yu Li Renzy](https://github.com/funkyela), [Jason Yao](https://github.com/JasonYao), [James Zhang](https://github.com/jamez852).

[Github repo](https://github.com/JasonYao/NLP-twitter-stock-trader).

## Description
This application will implement paper trading of stocks
based on a Natural Language Processing (NLP) algorithm
for sentiment analysis.

## Overview
The application has three main parts:

### Ingestion engine
The ingestion engine is the "front-end" of the application,
constantly running, utilising Twitter's [Streaming API](https://dev.twitter.com/streaming/overview)
to get the latest updates from important financial services
about stocks, before batching and passing the information
onto the SA engine.

If additional input is given to the ingestion engine while the
processing engine is busy, the ingestion engine will batch up
all input since the last batch, and then pass over all new input
as a single batch when the processing engine completes the last task.

This greatly increases efficiency, and allows the end user
to input as many lines of input as they wish (barring out
of memory exceptions).

### Sentiment Analysis (SA) engine
The SA engine parses the given input (tweets), combines it with
historical data, then computes and labels each given stock with
a `Viability Score` (`VS`). This score is calculated from the given
current sentiment about a stock, and its current position in the
marketplace, with a higher differential resulting in a higher
`VS`. Output will be saved in the [output/sentiment](output/sentiment/)
directory.

### (Paper) Trading engine
The Trading engine will take a given list of the highest `VS`
and proceed to [paper trade](https://en.wikipedia.org/wiki/Stock_market_simulator)
based off of the sentiment analysis. Output will be saved in
the [output/trading](output/trading/) directory.

### Runtime
TODO

## Running Commands
### To start the ingestion engine:
```sh
python ingest.py
```

### To bypass the Ingestion engine (generates sentiment analysis of a tweet directly):
```sh
python process.py path_to_input_file
```

e.g. With the sample input
```sh
python process.py sample_data.txt
```

### To bypass the Ingestion & SA engines (generates paper trades from a given SA)
```sh
python trade.py path_to_input_file
```

e.g. With the sample input
```sh
python trade.py sample_SA_data.txt
```

### To log in verbose mode
e.g. With sample input + verbose mode
```sh
python ingest.py sample_data.csv -v
# OR
python process.py --verbose sample_data.csv
```

### To see the help menu
```sh
python ingest.py -h
# OR
python process.py -h
# OR
python trade.py -h
```

## Dependencies
### Application Dependencies
- [Python 3](https://docs.python.org/3/) (developed & tested on 3.6.1)
- TODO

### Dev Dependencies (required to run tests)
- [pytest](http://doc.pytest.org/en/latest/)

## Installation
### OSX
Install Homebrew
```sh
/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
```

Install pyenv
```sh
brew install pyenv
echo 'eval "$(pyenv init -)"' >> ~/.bash_profile
```

Install Python 3
```sh
pyenv install 3.6.1
pyenv global 3.6.1
```

Install requirements
```sh
pip install -r requirements.txt
```

### Linux *
\* Installation instructions for Ubuntu 16.10 only

Install Python 3
```sh
sudo apt-get update
sudo apt-get install python3.6
```

Install requirements
```sh
pip3 install -r requirements.txt
```

## Testing
Testing utilises the [pytest](http://doc.pytest.org/en/latest/) framework,
and all tests can be executed via:
```sh
pytest tests.py -vs
```

## Logging
- Log files are stored in the [log](log/) directory.
- Program logs are automatically generated every time the
ingestion engine passes data to the processing engine.
- Log files are labeled by a time-stamp for easy ordering,
uniqueness, & analysis.
- Logging verbosity may be controlled with the `--verbose`
or `-v` flag passed into the command line when running either
the ingestion engine or processing engine. When verbose mode
is enabled in the ingestion engine, all subsequent batches
will also log in verbose mode.

## Efficiency optimisations
- Batches input in ingestion engine when processing engine
is still running from last batch
- Combining history with new input is also sped up by
saving historical data in a pre-parsed manner, and then adding new data
as appropriate. In this fashion, there is no need to re-parse historical
expressions.

## Potential Future Enhancements
- Utilise a database instead of saving to disk.
- Autogenerate gains/losses from current trading run segmented by time.
