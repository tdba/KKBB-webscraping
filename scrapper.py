#!/usr/bin/python3
# -*- coding: utf-8 -*-


from bs4 import BeautifulSoup
import requests

import sys
import json
import pickle


# ToTest with adequate connection
def max_page():
    url = 'https://www.kisskissbankbank.com/fr/discover?filter=all'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    print(soup.prettify())
    for i in soup.findAll('a'):
        print(i.text)


def links(max_p, current_page=1):
    res = []

    if current_page <= max_p:
        url = f'https://www.kisskissbankbank.com/fr/discover?filter=all&page={current_page}'
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")

        script = json.loads(soup.find('script', type="application/json", id=None, attrs={'class': None}).text)
        grid = script['BROWSING']['projects']['edges']
        for item in grid:
            res.append(item['node']['publicUrl'])

        print(f'Page {current_page} treated.')
        res += links(max_p, current_page+1)

    return res


def data_extraction(urls):
    res = []

    for url in urls:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")

        title = soup.find('h1', attrs={'data-test-id': 'project-title'}).text
        desc = soup.find('head').find('meta', attrs={'name': 'description'})['content']
        project_holder = soup.find('a', attrs={'class': "k-u-size-tiny k-u-weight-regular kiss-Link--primary1"})['href']

        print(soup.prettify())


if __name__ == '__main__':
    max_page = 1  # int(sys.argv[1])
    campaign_links = links(max_page)
    with open('links', mode='wb') as f:
        pickle.dump(campaign_links, f)
    data_extraction(["https://www.kisskissbankbank.com/fr/projects/des-fourmis-dans-les-mains-un-grand-feu"])  #links)
