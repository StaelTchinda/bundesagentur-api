# bundesagentur-api

This is an API to access to the databases of the German Federal Employment Agency (Deutsche Bundesagentur für Arbeit).

## Requirements

This repository is built on [Python 3.12](https://docs.python.org/3.12/).
In best case, create a virtual environment with the following command.

```
python -m venv venv
```

Activate the environment and install the required packages using:

```
pip install -r requirements.txt
```

## Tools

The API is built using [FastAPI](https://fastapi.tiangolo.com/). The code is structured following [the best practices](https://github.com/zhanymkanov/fastapi-best-practices?tab=readme-ov-file).

## Usage

To start the API, please run:

```
python -m scripts.main
```

To make the server restart after code changes, please run (only for development):

```
python -m scripts.main --reload
```

### Useful scripts

Since one benefit of this project is the ability to work with local data, it is important to easily fetch applicant profiles to store them locally. For this purpose, you can use the script `scripts/search_and_fetch_details.py`. One potential use is

````
python -m scripts.search_and_fetch_details --max_graduation_year 2000 --location_keyword "München" --pages_count 1
```
````
