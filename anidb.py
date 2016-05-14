#!/usr/bin/env python

import json
import os
from pprint import PrettyPrinter

import bs4

"""
Simple script for extracting AniDB title information from downloaded Season
Chart HTML pages.

Example URL that you need to download and place into a folder named `htmls/`
that should be created adjacent to the Python file `anidb.py`:

`https://anidb.net/perl-bin/animedb.pl?show=calendar`

The script loops through HTML files and their HTML elements and extract
information such as the anime's title, date, ratings, tags.

Output is a JSON file named `extracted_data.json`.

You must have the `BeautifulSoup4` module installed.
"""

__authors__ = ['Miha Jenko']

# for debug use
pprint = PrettyPrinter(indent=4).pprint

# open file folder
BASE_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), 'htmls'
)
files = os.listdir(BASE_DIR)

# loop through files
jsdata = {}
for fn in files:
    # skip non-html files
    if 'AniDB.htm' not in fn:
        continue

    # open page
    with open(os.path.join(BASE_DIR, fn), 'rb') as fp:
        page = fp.read()
        fp.close()

    # extract time information from filename
    print(fn)
    season, year = fn.split(' ')[3:5]
    year = year.split('_')
    try:
        year = year[1]
    except IndexError:
        year = year[0]
    jsdata[year] = {}
    jsdata[year][season] = []

    # HTML scraping
    soup = bs4.BeautifulSoup(page, 'html.parser')

    # loop through anime
    for anime in soup.select('.content .box'):
        anime_data = {}

        # anime title
        title = anime.select('.top .name .name-colored')[0]
        anime_data['title'] = title.text

        # air date
        data = anime.select('.data')[0]
        anime_data['date'] = data.select('.date')[0].text.strip('\n\t')

        # mean and average ratings
        anime_data['rating'] = {}
        ratings = data.find_all('div', class_='rating')
        mean_r = ratings[0].text.rstrip(' \n\t').split(' ')
        mean, mean_count = mean_r[0], mean_r[1][1:-1]
        avg_r = ratings[1].text.rstrip(' \n\t').split(' ')
        avg, avg_count = avg_r[0], avg_r[1][1:-1]
        anime_data['rating']['mean'] = {
            'value': mean,
            'count': mean_count
        }
        anime_data['rating']['avg'] = {
            'value': avg,
            'count': avg_count
        }

        # tags
        tags_acc = []
        for tag in anime.select('.tags')[0]:
            tag_info = {}
            try:
                tag_info = {
                    'tag': tag.a.span.text,
                    'description': tag.a.span.next_sibling.text
                }
                tags_acc.append(tag_info)
            except AttributeError:
                pass
        anime_data['tags'] = tags_acc

        jsdata[year][season].append(anime_data)

# save
save_fn = os.path.join(BASE_DIR, '..', 'extracted_data.json')
with open(save_fn, 'w') as fp:
    json.dump(jsdata, fp)
    fp.close()

# print final
try:
    pprint(jsdata)
except UnicodeEncodeError:
    pass
