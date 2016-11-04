#!encoding utf-8
from csv import DictWriter
from django.core.management.base import BaseCommand

import requests
import json


class Command(BaseCommand):
    def handle(self, *args, **options):
        print('Start.')

        res = self.request_holidays_for_date('now', 'x')
        holidays = res.copy()
        holidays['items'] = []

        for year in [2013, 2014, 2015, 2016]:
            print(year)
            holidays['items'] += self.request_holidays_for_date(year)['items']

        time_pairs = []

        for i, item in enumerate(holidays['items']):
            if item['category'] == 'candles':
                matching_havdalah_index = self.get_havdalah_index(holidays, i)
                if matching_havdalah_index == -1:
                    break
                pair = (item['date'], holidays['items'][matching_havdalah_index]['date'])
                time_pairs.append(pair)

        f = open('time_pairs.json', 'wb')
        json.dump(time_pairs, f)
        f.close()
        print('Done.')

    def get_havdalah_index(self, holidays, matching_havdalah_index):
        while not holidays['items'][matching_havdalah_index]['category'] == 'havdalah':
            matching_havdalah_index += 1
            if matching_havdalah_index >= len(holidays['items']):
                return -1
        return matching_havdalah_index

    def request_holidays_for_date(self, year, month='x'):
        url = "http://www.hebcal.com/hebcal/?v=1&cfg=json&maj=on&min=off&mod=on&nx=off&year={year}&month={month}&ss=off&mf=off&c=on&geo=geoname&geonameid=293397&m=50&s=off"
        res = requests.get(url.format(year=year, month=month))
        return res.json()
