#!/usr/bin/python3
# -*- coding: utf-8 -*-


import datetime as dt


class Campaign:
    def __init__(self, link, title, description, project_holder, current_amount, aimed_amount, end_date):
        self.link = link
        self.title = title
        self.description = description
        self.project_holder = project_holder
        self.current_amount = current_amount
        self.aimed_amount = aimed_amount
        self.achieved = aimed_amount <= current_amount

        if 'jour' in end_date or 'heure' in end_date:
            self.done = False
            if 'heure' in end_date:
                self.end_date = dt.date.today()
            else:
                d = dt.timedelta(days=int(end_date[:2].strip()))
                self.end_date = dt.date.today() + d
        else:
            self.end_date = dt.datetime.strptime(end_date, '%A, %B %d, %Y').date()
            self.done = end_date <= dt.date.today()

        self.actualities = []
        self.donations = []
        self.contributors = []

    def add_donation(self, donation):
        if donation.user not in self.contributors:
            self.contributors.append(donation.user)
        self.donatiosn.append(donation)


class Donation:
    def __init__(self, user, amount, date):
        self.user = user
        self.amount = amount
        self.date = date


class News:
    def __init__(self, title, content, date, kind=None):
        self.title = title
        self.content = content
        self.date = dt.datetime.strptime(date, '%A, %B %d, %Y').date()
        self.kind = kind
