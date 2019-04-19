#!/usr/bin/python3
# -*- coding: utf-8 -*-


class Campaign:
    def __init__(self, link, title, description, project_holder, current_amount, aimed_amount, start_date, end_date):
        self.link = link
        self.title = title
        self.description = description
        self.project_holder = project_holder
        self.current_amount = current_amount
        self.aimed_amount = aimed_amount
        self.start_date = start_date
        self.end_date = end_date
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
    def __init__(self, content, date):
        self.content = content
        self.date = date
