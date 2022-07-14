from lxml import html
import numpy as np
import pandas as pd  
import requests 

def run(title_id ='tt0096697', num_seasons = 1):
    dataframe = pd.DataFrame()
    for i in range(1,num_seasons+1):  # the second value of range is the index, not value
        url = f'https://www.imdb.com/title/{title_id}/episodes?season={i}'

        r = requests.get(url)

        tree = html.fromstring(r.text)
        description_rows =  tree.xpath('//div[@class="item_description"]')  # had to remove /text() because it was splitting on <a> tags and creating extra rows
        title_rows = tree.xpath('//div[@class="info"]/strong/a/text()')
        airdate_rows = tree.xpath('//div[@class="info"]/div[@class="airdate"]/text()')
        rating_rows = tree.xpath('//div[@class="info"]/div[@class="ipl-rating-widget"]/div[@class="ipl-rating-star small"]/span[@class="ipl-rating-star__rating"]/text()')
        ratingcount_rows = tree.xpath('//div[@class="info"]/div[@class="ipl-rating-widget"]//span[@class="ipl-rating-star__total-votes"]/text()')

        titles = [title for title in title_rows]
        descriptions = [description.xpath('text()')[0].strip() for description in description_rows] # grab first element of list from xpath to dig into div
        airdates = [airdate.strip() for airdate in airdate_rows] # format: (n,nnn) -> nnnn
        ratings = [rating for rating in rating_rows]
        num_ratings = [count.replace(',','').replace('(','').replace(')', '') for count in ratingcount_rows]
        # convert airdates to ISO-8601

        dataframe = dataframe.append(pd.DataFrame({'season':np.full((len(titles)), i, dtype=int),
                                                'title': titles,
                                                'airdate': airdates,
                                                'description': descriptions,
                                                'rating': ratings,
                                                'num_ratings':num_ratings}))

    print(dataframe.to_csv(index=False))


if __name__ == '__main__':
    title_id ='tt0096697' # The Simpsons
    num_seasons = 33 # skip current season as it doesn't have ratings data
    run(title_id, num_seasons)
