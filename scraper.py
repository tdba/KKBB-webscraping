#!/usr/bin/python3
# -*- coding: utf-8 -*-


from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


from time import sleep
from random import randint
import pandas as pd
import pickle

import campaign


URL = "https://www.kisskissbankbank.com"


def info_extraction(link, cats):
    response = requests.get(link + '/tabs/description')
    sleep(randint(0, 4))
    while response.status_code != 200:
        response = requests.get(link + '/tabs/description')
        sleep(randint(0, 4))
    soup = BeautifulSoup(response.content, 'html5lib')

    title = soup.find('h1', attrs={'data-test-id': 'project-title'}).text
    project_holder = URL + soup.find('div', class_='intro__StyledOwner-sc-1wfo5yh-8 iEVesU').a['href']
    desc = soup.find('head').find('meta', attrs={'name': 'description'})['content']

    completion_rate = int(soup.find('div', class_='progress__StyledText-ycznm1-1').text[:3])
    prompt = soup.find_all('div', class_='clfvNf')
    sub_prompt = soup.find_all('div', class_='gDdVEG')

    nb_contrib = int(prompt[0].text.strip().replace(u'\xa0', u''))
    end_date = prompt[1].text
    try:
        actual_value = int(prompt[2].text[:-1].strip().replace(u'\xa0', u''))
        aimed_value = int(sub_prompt[2].text[3:-1].strip().replace(u'\xa0', u''))
    except ValueError:
        actual_value, aimed_value = 'No monetary information', 'No monetary information'
    return campaign.Campaign(link, title, desc, project_holder, actual_value, aimed_value, end_date, nb_contrib,
                             completion_rate, cats)


def actualities_extraction(p):
    response = requests.get(p.link + '/tabs/news')
    sleep(randint(0, 4))
    while response.status_code != 200:
        response = requests.get(p.link + '/tabs/news')
        sleep(randint(0, 4))
    soup = BeautifulSoup(response.content, 'html5lib')
    news = soup.select('div.marger__StyledMarger-q3lecu-0.denjnR')
    if news[0].section:
        for item in news:
            date = item.select_one('div.marger__StyledMarger-q3lecu-0.jgfcQX > span').text
            news_title = item.find('h3').text
            content = item.find_all('div')[1].text
            actuality = campaign.News(news_title, content, date)
            p.actualities.append(actuality)


def highest_reward_price_extraction(p):
    response = requests.get(p.link + '/tabs/rewards')
    sleep(randint(0, 4))
    while response.status_code != 200:
        response = requests.get(p.link + '/tabs/rewards')
        sleep(randint(0, 4))
    soup = BeautifulSoup(response.content, 'html5lib')

    reward_class = 'k-TitleWithStroke__title k-TitleWithStroke__title--senary'

    p.hrp = max([int(e.string[5:-2].strip().replace(u'\xa0', u'')) for e in soup.find_all('h2', class_=reward_class)])


def other_projects_extraction(p):
    response = requests.get(p.project_holder)
    sleep(randint(0, 4))
    while response.status_code != 200:
        response = requests.get(p.project_holder)
        sleep(randint(0, 4))
    soup = BeautifulSoup(response.content, 'html5lib')

    p.other_projects = len(soup.find_all('div', class_='project')) > 1


def display_all(wait):
    sleep(2)
    try:
        button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[text()='En voir plus']")))
        while button:
            button.click()
            button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[text()='En voir plus']")))
    except TimeoutException:
        pass


def donations_extraction(p, browser, wait):
    browser.get(p.link + '/tabs/backers')
    display_all(wait)

    inner_html = browser.execute_script("return document.body.innerHTML")
    soup = BeautifulSoup(inner_html, 'html5lib')

    for item in soup.select('div.backer-card__StyledCard-zl7grf-0.hSpaUR'):
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


def coms_extraction(p, browser, wait):
    browser.get(p.link + '/tabs/comments')
    display_all(wait)

    inner_html = browser.execute_script("return document.body.innerHTML")
    soup = BeautifulSoup(inner_html, 'html5lib')

    p.comments = []

    p_holder = soup.find('div', class_='k-u-weight-regular owner-info__StyledOwnerName-tqxc8c-6 dyAQdt').string

    for com in soup.select('div.comment__StyledGrid-sc-8s8e85-2.iFjxIp'):
        author = com.select_one('span > div > div > span').string
        delay = com.select_one('span.k-u-color-font1.k-u-size-micro.k-u-weight-light').string
        if any(ti in delay for ti in ['minute', 'heure']):
            ddelay = 1
        else:
            ddelay = int(delay.split()[0])

        if author != p_holder:
            p.comments.append((pd.to_datetime('today') - pd.to_timedelta(ddelay, 'days')).date())


def data_extraction(df):

    res = []

    for i, row in df.iterrows():
        print(f'Project {i}: {row.url} scrapping.')
        try:
            project = info_extraction(row.url, row.cats)
            actualities_extraction(project)

            res.append(project)
        except IndexError:
            print(f'Fail on project {i}: {row.url} scraping.')

    return res


def select_data_extraction(projects):
    driver = webdriver.Chrome(ChromeDriverManager().install())
    wait = WebDriverWait(driver, 2)

    for i, project in enumerate(projects):
        print(f'Project {i}: {project.link} scraping.')
        highest_reward_price_extraction(project)
        other_projects_extraction(project)
        donations_extraction(project, driver, wait)
        coms_extraction(project, driver, wait)

    driver.close()


if __name__ == '__main__':
    ex_type = input('Init? (y/n)').lower()
    if ex_type == 'y':
        links = pd.read_pickle('data/links.pkl')
        links = links.loc[:22000]
        camp_list = data_extraction(links)

        with open('data/campaigns.pkl', 'wb') as f:
            pickle.dump(camp_list, f)

    else:
        with open('data/selected_campaigns.pkl', 'rb') as f:
            campaigns = pickle.load(f)

        select_data_extraction(campaigns)

        with open('data/filled_selected_campaigns.pkl', 'wb') as f:
            pickle.dump(campaigns, f)

