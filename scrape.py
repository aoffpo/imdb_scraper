#!/usr/bin/env python3

# pylint: disable=C0301
# pylint: disable=fixme
# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring


import sys
import getopt
from lxml import html
import numpy as np
import pandas as pd
import requests


def get_episodes(title_id='tt0096697', num_seasons=1):
    print('Scraping Episode Data...')

    dataframe = pd.DataFrame()
    for i in range(1, num_seasons + 1):  # the second value of range is the index, not value
        url = f'https://www.imdb.com/title/{title_id}/episodes?season={i}'

        request = requests.get(url)

        tree = html.fromstring(request.text)
        # had to remove /text() because it was splitting on <a> tags and creating extra rows
        description_rows = tree.xpath('//div[@class="item_description"]')
        title_rows = tree.xpath('//div[@class="info"]/strong/a/text()')
        airdate_rows = tree.xpath('//div[@class="info"]/div[@class="airdate"]/text()')
        rating_rows = tree.xpath('//div[@class="info"]/div[@class="ipl-rating-widget"]/div[@class="ipl-rating-star small"]/span[@class="ipl-rating-star__rating"]/text()')  # nopep8
        ratingcount_rows = tree.xpath('//div[@class="info"]/div[@class="ipl-rating-widget"]//span[@class="ipl-rating-star__total-votes"]/text()')  # nopep8

        titles = [title for title in title_rows]
        # grab first element of list from xpath to dig into div
        descriptions = [description.xpath('text()')[0].strip() for description in description_rows]
        airdates = [airdate.strip() for airdate in airdate_rows]  # TODO: convert airdates to ISO-8601
        ratings = [rating for rating in rating_rows]
        # format: (n,nnn) -> nnnn
        num_ratings = [count.replace(',', '').replace('(', '').replace(')', '') for count in ratingcount_rows]

        dataframe = dataframe.append(pd.DataFrame({'season': np.full((len(titles)), i, dtype=int),
                                                   'title': titles,
                                                   'airdate': airdates,
                                                   'description': descriptions,
                                                   'rating': ratings,
                                                   'num_ratings': num_ratings}))
    return dataframe


def get_cast(title_id):
    print('Scraping Cast Data...')
    url = f'https://www.imdb.com/title/{title_id}/fullcredits/'
    request = requests.get(url)
    tree = html.fromstring(request.text)
    # get all credit type names
    job_type_rows = tree.xpath('//h4/@id')

    dataframe = pd.DataFrame()
    for job_type in job_type_rows:
        name_expr = f'//h4[@id="{job_type}"]/following-sibling::table[1]//td[@class="name"]//a/text()'
        name_list = [name.strip() for name in tree.xpath(name_expr)]
        credit_expr = f'//h4[@id="{job_type}"]/following-sibling::table[1]//td[@class="credit"]/text()'
        credit_list = [credit.strip() for credit in tree.xpath(credit_expr)]
        dataframe = dataframe.append(pd.DataFrame({'credit_type': np.full((len(name_list)), job_type),
                                                   'name': name_list,
                                                   'credit': credit_list}))
    return dataframe


# //div[@id="filmography"]//a/text()[contains(.,"The Simpsons")]
def get_cast_details():
    pass


def get_arguments():
    episodes_flag = False
    cast_flag = False
    argument_list = sys.argv[1:]
    options = 'hce'
    long_options = ['Help', 'Cast', 'Episodes']
    arguments, values = getopt.getopt(argument_list, options, long_options)  # pylint: disable=unused-variable
    try:
        for current_argument, current_value in arguments:  # pylint: disable=unused-variable
            if current_argument in ('-h', '--Help'):
                print('Scrape Episodes (-e), Cast (-c) or both (-ec) or show this help (-h)')
            elif current_argument in ('-c', '--Cast'):
                cast_flag = True
            elif current_argument in ('-e', '--Episodes'):
                episodes_flag = True
    except getopt.error as err:
        print(str(err))

    return cast_flag, episodes_flag


if __name__ == '__main__':
    cast, episodes = get_arguments()
    TITLE_ID = 'tt0096697'  # The Simpsons
    NUMSEASONS = 33  # skip current season as it doesn't have ratings data

    if cast:
        df_cast = get_cast(TITLE_ID)
        df_cast.to_csv('cast.csv', index=False)
    if episodes:
        df_episodes = get_episodes(TITLE_ID, NUMSEASONS)
        df_episodes.to_csv('episodes.csv', index=False)
