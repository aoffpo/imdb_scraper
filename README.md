# imdb_scraper

Python 3.7.9
Usage: comment out get_cast or get_episodes

`python3 scrape.py > [cast.csv | episodes.csv]`

cast has columns: credit_type, name, credit
episodes has columns:season, 'title',  'airdate', 'description', 'rating', 'num_ratings

edit scrape.py entrypoint to set imdb series id and number of seasons to scrape.
Use default (1 season) for debugging.

TODO: xpath not great.
TODO: convert dates to ISO-8601
TODO: cli switches for each type of csv that can be generated or write to file instead of print
