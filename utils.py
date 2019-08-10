#!/usr/bin/python3
# -*- coding: utf-8 -*-


import pickle
import csv
import datetime
from itertools import groupby
from operator import itemgetter

import campaign


STIMULI = ['continuez', 'partager', 'partagez', 'on compte sur vous', 'parlez', 'likez', 'contribuer', 'contribuez',
           'aidez', 'soutenez', 'share', 'likez', 'donnez', 'persuadez', 'j-']


def classify(num):
    return {0: 'Post fin de campagne', 1: 'Informatif', 2: 'Persuasif'}[num]


def verify(num, state):
    if num == 0:
        return {'Persuasif': 'Informatif', 'Informatif': 'Persuasif'}[state]
    else:
        return state


"""
with open('campaigns', 'rb') as f:
    campaigns = pickle.load(f)

selected = sorted(campaigns, key=lambda project: len(project.actualities), reverse=True)[:200]

with open('selected', 'wb') as f:
    pickle.dump(selected, f)
"""


def classification(campaigns):
    for c in campaigns:
        for actu in c.actualities:
            if actu.date > c.end_date:
                actu.kind = classify(0)
            else:
                if any(stimulus in text for stimulus in STIMULI for text in [actu.content.lower(), actu.title.lower()]):
                    actu.kind = classify(2)
                else:
                    pass
                    # actu.kind = classify(1)


def verification(campaigns):
    for i, c in enumerate(campaigns):
        print(f'CAMPAIGN {i}\n------------\n')
        print(c.title.upper() + '\n')
        print(str(c.end_date) + '\n')
        print(c.description + '\n\n')
        for actu in c.actualities:
            print('-----\n')
            if actu.kind != classify(0):
                print(actu.kind)
                print(actu.title.upper())
                print(actu.content)
                try:
                    actu.kind = verify(int(input()), actu.kind)
                except:
                    pass

        print('\n\n\n')


def store(campaigns):
    with open('news_classification.csv', mode='w+') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        csv_writer.writerow(['Campagne/Actualité', 'Titre', 'Description', 'Date de fin/parution', "Type d'actualité"])
        for c in campaigns:
            csv_writer.writerow(['C', c.title, c.description, str(c.end_date)])
            for actu in c.actualities:
                csv_writer.writerow([' ', actu.title, actu.content, str(actu.date), actu.kind])


def store_campaigns_data(campaigns):
    with open('data/campaigns_data.csv', mode='w+') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(['Campagne', 'NInfo', 'NPers', 'NDon', "NJump", "Amount"])

        for c in campaigns:
            n_pers = 0
            n_info = 0
            for actu in c.actualities:
                if actu.kind == 'Informatif':
                    n_info += 1
                elif actu.kind == 'Persuasif':
                    n_pers += 1

            try:
                min_don = min(c.donations, key=lambda x: x.amount).amount
            except:
                continue
            n_jump = 0
            for don in c.donations:
                if don.amount > min_don:
                    n_jump += 1
            csv_writer.writerow([c.link, n_info, n_pers, len(c.donations), n_jump, c.current_amount])


def store_donations_data(campaigns):
    with open('data/donations_data.csv', mode='w+') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(['Campagne', 'Jump', 'PersJ-1', 'InfoJ-1', 'NDonations'])

        for c in campaigns:
            try:
                min_don = min(c.donations, key=lambda x: x.amount).amount
            except:
                continue
            events = [(e.date, e) for e in sorted(c.actualities + c.donations, key=lambda x: x.date)]
            grouped_events = [(k, [x for _, x in g]) for k, g in groupby(events, itemgetter(0))]
            grouped_events[:] = [events for events in grouped_events if events[0] <= c.end_date]

            pers = False
            info = False
            donation = False
            number_donations = 0
            for events_by_date in grouped_events:
                if donation:
                    pers = False
                    info = False
                    donation = False
                for e in events_by_date[1]:
                    if type(e) is campaign.News:
                        if e.kind == 'Informatif':
                            info = True
                        if e.kind == 'Persuasif':
                            pers = True

                    if type(e) is campaign.Donation:
                        donation = True
                        number_donations += 1
                        jump = e.amount > min_don
                        csv_writer.writerow([c.link, int(jump), int(info), int(pers), number_donations])


def store_messages_data(campaigns, kind):
    with open(f'data/{kind}_messages_data.csv', mode='w+') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(['Campagne', kind, 'PersJ-1', 'InfoJ-1', 'NDon'])

        for c in campaigns:
            if len(c.donations) == 0:
                continue
            events = [(e.date, e) for e in sorted(c.actualities + c.donations, key=lambda x: x.date)]
            grouped_events = [(k, [x for _, x in g]) for k, g in groupby(events, itemgetter(0))]
            grouped_events[:] = [events for events in grouped_events if events[0] <= c.end_date]

            pers = False
            info = False
            donation = False
            published = False
            number_donations = 0
            for events_by_date in grouped_events:

                if donation:
                    if not published:
                        csv_writer.writerow([c.link, 0, int(info), int(pers), number_donations])
                    published = False
                    pers = False
                    info = False
                    donation = False
                for e in events_by_date[1]:
                    if type(e) is campaign.News:
                        if e.kind == kind:
                            published = True
                            csv_writer.writerow([c.link, 1, int(info), int(pers), number_donations])
                        if e.kind == 'Informatif':
                            info = True
                        if e.kind == 'Persuasif':
                            pers = True

                    if type(e) is campaign.Donation:
                        donation = True
                        number_donations += 1
            if donation and not published:
                csv_writer.writerow([c.link, 0, int(info), int(pers), number_donations])


if __name__ == '__main__':
    with open('data/classified', 'rb') as f:
        projects = pickle.load(f)

    classification(projects)
    # verification(projects)
    # store(projects)
    # store_campaigns_data(projects)

    store_donations_data(projects)
    store_messages_data(projects, 'Informatif')
    store_messages_data(projects, 'Persuasif')

    with open('data/classified', 'wb') as f:
        pickle.dump(projects, f)
