#!/usr/bin/python3
# -*- coding: utf-8 -*-


import datetime as dt
import dateparser


class Campaign:
    def __init__(self, link, title, description, project_holder, current_amount, aimed_amount, end_date):
        self.link = link
        self.title = title
        self.description = description
        self.project_holder = project_holder
        self.current_amount = current_amount
        self.aimed_amount = aimed_amount
        self.achieved = aimed_amount <= current_amount

        if 'jour' in end_date or 'heure' in end_date or 'minute' in end_date:
            self.done = False
            if 'jour' in end_date:
                d = dt.timedelta(days=int(end_date[:2].strip()))
                self.end_date = dt.date.today() + d
            else:
                self.end_date = dt.date.today()
        else:
            self.end_date = dt.datetime.strptime(end_date, '%A, %B %d, %Y').date()
            self.done = self.end_date <= dt.date.today()

        self.actualities = []
        self.donations = []
        self.contributors = []

    def add_donation(self, donation):
        if donation.user not in self.contributors:
            self.contributors.append(donation.user)
        self.donations.append(donation)


class Donation:
    def __init__(self, user, date, amount=0):
        self.user = user
        self.amount = amount
        self.date = dateparser.parse(date).date()


class News:
    def __init__(self, title, content, date, kind=None):
        self.title = title
        self.content = content
        self.date = dt.datetime.strptime(date, '%A, %B %d, %Y').date()
        self.kind = kind
