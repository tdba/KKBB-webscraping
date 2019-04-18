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

        res += links(max_p, current_page+1)

    return res


if __name__ == '__main__':
    max_page = int(sys.argv[1])
    for item in links(max_page):
        print(item)
