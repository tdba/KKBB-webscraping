#!/usr/bin/python3
# -*- coding: utf-8 -*-


from bs4 import BeautifulSoup
import requests
from requests_html import HTMLSession
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

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

        sleep(randint(0, 4))
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
    def info_extraction(link):
        response = requests.get(link + '/tabs/description')
        soup = BeautifulSoup(response.content, 'html5lib')

        title = soup.find('h1', attrs={'data-test-id': 'project-title'}).text
        desc = soup.find('head').find('meta', attrs={'name': 'description'})['content']
        project_holder = URL + soup.find('div', class_='owner-info__StyledOwner-sc-1r3rkij-2 gDZNgQ').a['href']

        prompt_class = 'informations-and-media__StyledInfo-sc-121rta3-3 fzHbGm marger__StyledMarger-q3lecu-0 hAgZUM'
        prompt = soup.find_all('div', class_=prompt_class)[1:]
        end_date = prompt[0].div.text
        values = prompt[1].find_all('div')
        try:
            actual_value = int(values[0].text[:-1].strip().replace(u'\xa0', u''))
            aimed_value = int(values[1].text[3:-1].strip().replace(u'\xa0', u''))
        except ValueError:
            actual_value, aimed_value = 0, 0

        return campaign.Campaign(url, title, desc, project_holder, actual_value, aimed_value, end_date)

    def actualities_extraction(p):
        resp = requests.get(p.link + '/tabs/news')
        soup = BeautifulSoup(resp.content, 'html5lib')
        news = soup.select('div.marger__StyledMarger-q3lecu-0.denjnR')
        if news[0].section:
            for item in news:
                date = item.select_one('div.marger__StyledMarger-q3lecu-0.jgfcQX > span').text
                news_title = item.find('h1').text
                content = item.select_one('div.kiss-RichText.marger__StyledMarger-q3lecu-0.WSKaG > div').text
                actuality = campaign.News(news_title, content, date)
                p.actualities.append(actuality)

    def donations_extractions(p, browser):
        browser.get(p.link + '/tabs/backers')
        try:
            button = browser.find_element_by_xpath("//button[text()='En voir plus']")
            while button:
                browser.execute_script("arguments[0].click();", button)
                sleep(0.4)
                button = browser.find_element_by_xpath("//button[text()='En voir plus']")
        except NoSuchElementException:
            pass

        innerHTML = browser.execute_script("return document.body.innerHTML")
        soup = BeautifulSoup(innerHTML, 'html5lib')
        for item in soup.select('div.backers-list__StyledCard-sc-13o55g1-1.gKLrNb'):
            user = item.select_one('div > span').text
            gift = item.select('div.marger__StyledMarger-q3lecu-0.bsSajs > p > span')
            if len(gift) == 2:
                amount = int(gift[0].text[:-1].strip().replace(u'\xa0', u''))
                date = gift[1].text.strip()
                donation = campaign.Donation(user, date, amount)
            else:
                date = gift[0].text.strip()
                donation = campaign.Donation(user, date)
            p.add_donation(donation)

    res = []
    driver = webdriver.Chrome()

    for url in urls:
        project = info_extraction(url)
        actualities_extraction(project)
        donations_extractions(project, driver)

        res.append(project)
        print(f'Project {project.title} treated.')
        sleep(randint(0, 2))

    driver.close()
    return res


if __name__ == '__main__':
    # max_page = max_page()
    # campaign_links = links(max_page)
    # with open('links', 'wb') as f:
    #     pickle.dump(campaign_links, f)

    with open('links', 'rb') as f:
        campaign_links = pickle.load(f)
    campaigns = data_extraction(campaign_links)
    with open('campaigns', 'wb') as f:
        pickle.dump(campaigns, f)
