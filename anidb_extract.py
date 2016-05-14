#!/usr/bin/env python

import json
import os
import sys

import bs4

"""
Reffer to README.md for instructions.
"""

__authors__ = ['Miha Jenko']

# open file folder
try:
    BASE_DIR = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), sys.argv[1]
    )
except IndexError:
    sys.exit('ERROR: HTML folder argument missing')

try:
    files = os.listdir(BASE_DIR)
except FileNotFoundError:
    sys.exit('ERROR: HTML folder does not exist')

# loop through files
jsdata = {}
for fn in files:
    # open page
    with open(os.path.join(BASE_DIR, fn), 'rb') as fp:
        page = fp.read()

    # HTML scraping
    soup = bs4.BeautifulSoup(page, 'html.parser')

    # extract time information from filename
    print('Processing file: ', fn)
    season, year = soup.select('h1.calendar')[0].text.split(' ')[3:5]
    year = year.split('/')
    season = season.lower()
    try:
        year = year[1]
    except IndexError:
        year = year[0]

    try:
        jsdata[year][season] = []
    except KeyError:
        jsdata[year] = {
            season: []
        }

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

    print('{0} {1}, number of titles: {2} '.format(
          year, season, len(jsdata[year][season])))


# save
try:
    save_name = sys.argv[2]
except IndexError:
    save_name = 'extracted_data.json'

save_fn = os.path.join(BASE_DIR, '..', save_name)
with open(save_fn, 'w', encoding='utf-8', errors='xmlcharrefreplace') as fp:
    json.dump(jsdata, fp)
