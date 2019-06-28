#!/usr/bin/python3
# -*- coding: utf-8 -*-


from bs4 import BeautifulSoup
import requests

from time import sleep
from random import randint
from math import ceil
import json
import pickle

import campaign


URL = 'https://www.kisskissbankbank.com'


def max_page():
    url = URL + '/fr/discover?filter=all'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html5lib")

    script = json.loads(soup.find('script', class_='js-react-on-rails-component').text)
    nb_projects = script['BROWSING']['projects']['totalCount']

    return ceil(nb_projects/9)


def links(max_p, current_page=1):
    res = []

    while current_page <= max_p:
        url = URL + f'/fr/discover?filter=all&page={current_page}'
        response = requests.get(url)

        sleep(randint(8, 15))
        while response.status_code != 200:
            response = requests.get(url)
            sleep(randint(0, 4))
            print('Request not treated')

        soup = BeautifulSoup(response.content, 'html5lib')

        script = json.loads(soup.find('script', class_='js-react-on-rails-component').text)
        grid = script['BROWSING']['projects']['edges']

        for item in grid:
            res.append(item['node']['publicUrl'])

        print(f'Page {current_page} treated.')
        current_page += 1

    return res


def data_extraction(urls):
    res = []

    for url in urls:
        response = requests.get(url + '/tabs/description')
        soup = BeautifulSoup(response.content, 'html5lib')

        title = soup.find('h1', attrs={'data-test-id': 'project-title'}).text
        desc = soup.find('head').find('meta', attrs={'name': 'description'})['content']
        project_holder = URL + soup.find('div', class_='owner-info__StyledOwner-sc-1r3rkij-2 gDZNgQ').a['href']
        print(soup.head)

    return res


if __name__ == '__main__':
    max_page = max_page()
    campaign_links = links(max_page)
    with open('links', 'wb') as f:
        pickle.dump(campaign_links, f)

    #with open('links', 'rb') as f:
    #    campaign_links = pickle.
    #data_extraction(['https://www.kisskissbankbank.com/fr/projects/timada-une-expedition-scientifique-etudiante-au-coeur-de-madagascar'])#campaign_links)
