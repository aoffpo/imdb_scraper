from lxml import html
import numpy as np
import pandas as pd
import requests


def get_episodes(title_id='tt0096697', num_seasons=1):
    dataframe = pd.DataFrame()
    for i in range(1, num_seasons + 1):  # the second value of range is the index, not value
        url = f'https://www.imdb.com/title/{title_id}/episodes?season={i}'

        request = requests.get(url)

        tree = html.fromstring(request.text)
        # had to remove /text() because it was splitting on <a> tags and creating extra rows
        description_rows = tree.xpath('//div[@class="item_description"]')
        title_rows = tree.xpath('//div[@class="info"]/strong/a/text()')
        airdate_rows = tree.xpath('//div[@class="info"]/div[@class="airdate"]/text()')
        rating_rows = tree.xpath('//div[@class="info"]/div[@class="ipl-rating-widget"]/div[@class="ipl-rating-star small"]/span[@class="ipl-rating-star__rating"]/text()')
        ratingcount_rows = tree.xpath('//div[@class="info"]/div[@class="ipl-rating-widget"]//span[@class="ipl-rating-star__total-votes"]/text()')

        titles = [title for title in title_rows]
        # grab first element of list from xpath to dig into div
        descriptions = [description.xpath('text()')[0].strip() for description in description_rows]
        airdates = [airdate.strip() for airdate in airdate_rows]  # TODO: convert airdates to ISO-8601
        ratings = [rating for rating in rating_rows]
        # format: (n,nnn) -> nnnn
        num_ratings = [count.replace(',', '').replace('(', '').replace(')', '') for count in ratingcount_rows]  # nopep8

        dataframe = dataframe.append(pd.DataFrame({'season': np.full((len(titles)), i, dtype=int),
                                                   'title': titles,
                                                   'airdate': airdates,
                                                   'description': descriptions,
                                                   'rating': ratings,
                                                   'num_ratings': num_ratings}))

    print(dataframe.to_csv(index=False))


def get_cast(title_id):
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
    print(dataframe.to_csv(index=False))


if __name__ == '__main__':
    TITLE_ID = 'tt0096697'  # The Simpsons
    NUMSEASONS = 33  # skip current season as it doesn't have ratings data

    get_cast(TITLE_ID)
    get_episodes(TITLE_ID, NUMSEASONS)
