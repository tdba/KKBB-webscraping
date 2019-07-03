#!/usr/bin/python3
# -*- coding: utf-8 -*-


from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

from time import sleep
from random import randint
from math import ceil
from copy import deepcopy
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


def data_extraction(urls, untreated_url):
    def info_extraction(link):
        response = requests.get(link + '/tabs/description')
        soup = BeautifulSoup(response.content, 'html5lib')

        title = soup.find('head').find('title').text
        desc = soup.find('head').find('meta', attrs={'name': 'description'})['content']
        project_holder = URL + soup.select_one('div.owner-info__StyledOwner-sc-1r3rkij-2.gDZNgQ').a['href']

        prompt_class = 'informations-and-media__StyledInfo-sc-121rta3-3 fzHbGm marger__StyledMarger-q3lecu-0 hAgZUM'
        prompt = soup.find_all('div', class_=prompt_class)[1:]
        end_date = prompt[0].div.text
        values = prompt[1].find_all('div')
        try:
            actual_value = int(values[0].text[:-1].strip().replace(u'\xa0', u''))
            aimed_value = int(values[1].text[3:-1].strip().replace(u'\xa0', u''))
        except ValueError:
            actual_value, aimed_value = 'No monetary information', 'No monetary information'

        return campaign.Campaign(link, title, desc, project_holder, actual_value, aimed_value, end_date)

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
                sleep(0.2)
                button = browser.find_element_by_xpath("//button[text()='En voir plus']")
        except NoSuchElementException:
            pass

        inner_html = browser.execute_script("return document.body.innerHTML")
        soup = BeautifulSoup(inner_html, 'html5lib')
        for item in soup.select('div.backers-list__StyledCard-sc-13o55g1-1.gKLrNb'):
            user = item.select_one('div > span').text
            gift = item.select('div.marger__StyledMarger-q3lecu-0.bsSajs > p > span')

            if len(gift) == 2:
                try:
                    amount = int(gift[0].text[:-1].strip().replace(u'\xa0', u''))
                except ValueError:
                    amount = 'No monetary information'

                date = gift[1].text.strip()
                donation = campaign.Donation(user, date, amount)
            else:
                date = gift[0].text.strip()
                donation = campaign.Donation(user, date)
            p.add_donation(donation)

    res = []
    driver = webdriver.Chrome()
    i = 1

    while urls:
        try:
            print(f'Project {i}: {urls[0]} scrapping.')
            project = info_extraction(urls[0])
            actualities_extraction(project)
            donations_extractions(project, driver)

            res.append(project)
            i += 1
            sleep(randint(0, 2))
        except:
            pass

        del(urls[0])

    driver.close()
    return res


if __name__ == '__main__':
    # max_page = max_page()
    # campaign_links = links(max_page)
    # with open('links', 'wb') as f:
    #     pickle.dump(campaign_links, f)

    with open('links', 'rb') as f:
        campaign_links = pickle.load(f)

    while campaign_links:
        print(len(campaign_links))
        number_to_treat = 100
        treated_campaigns = []
        campaign_links_to_treat = deepcopy(campaign_links[:number_to_treat])
        while campaign_links_to_treat:
            campaigns = data_extraction(campaign_links_to_treat, [])
            treated_campaigns.extend(campaigns)

        with open('links', 'wb') as f:
            pickle.dump(campaign_links[number_to_treat:], f)

        campaign_links = campaign_links[number_to_treat:]

        with open('campaigns', 'rb') as f:
            stored_campaigns = pickle.load(f)
        treated_campaigns.extend(stored_campaigns)
        with open('campaigns', 'wb') as f:
            pickle.dump(treated_campaigns, f)
