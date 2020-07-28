#!/usr/bin/python3
# -*- coding: utf-8 -*-


import datetime as dt
import dateparser


class Campaign:
    def __init__(self, link, title, description, project_holder, current_amount, aimed_amount, end_date, nb_contrib,
                 completion_rate, categories):
        self.link = link
        self.title = title
        self.description = description
        self.project_holder = project_holder
        self.current_amount = current_amount
        self.aimed_amount = aimed_amount
        self.nb_contrib = nb_contrib
        self.completion_rate = completion_rate
        self.categories = categories
        self.num_pers = 0
        self.num_info = 0
        self.hrp = 0
        self.other_projects = False

        self.end_date = dt.datetime.strptime(end_date, '%d/%m/%Y').date()

        self.actualities = []
        self.donations = []
        self.contributors = []
        self.comments = []

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
        self.date = dateparser.parse(date).date()
        self.kind = kind
