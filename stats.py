#!/usr/bin/env python

import json
import pickle
import sys

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

"""
Reffer to README.md for instructions.
"""

# check for JSON filename in arguments, or default to 'extracted_data.json'
try:
    js_name = sys.argv[1]
except IndexError:
    js_name = 'extracted_data.json'

# open JSON file
with open(js_name, 'r') as f:
    data = json.load(f)

# get total anime title number, total tag number, build a tag reference dict
anime_n = 0
tag_n = 0
tags_dict = {}
for year, v in data.items():
    for season, anime in v.items():
        anime_n += len(anime)
        for an in anime:
            tags = an['tags']
            for tag in tags:
                try:
                    name = tags_dict[tag['tag']]
                except KeyError:
                    tags_dict[tag['tag']] = [
                        tag_n, tag['description']
                    ]
                    tag_n += 1

# anime-tag count matrix
at = np.zeros((anime_n, tag_n))
# compare matrix
sim_mat = np.zeros((anime_n, anime_n))

# fill up anime-tag matrix, build a anime reference dict
anime_dict = {}
i = 0
for year, v in data.items():
    for season, anime in v.items():
        for an in anime:
            anime_dict[an['title']] = i
            tags = an['tags']
            for tag in tags:
                at[i, tags_dict[tag['tag']][0]] = 1
            i += 1

# compare anime vectors with cosine similarity and build similarity matrix
sim_mat = cosine_similarity(at)
print('Anime-Tag matrix shape:', at.shape)
print('Similarity matrix shape:', sim_mat.shape)

# save to pickles
with open('at.pkl', 'wb') as fp:
    pickle.dump(at, fp)
with open('sim_mat.pkl', 'wb') as fp:
    pickle.dump(sim_mat, fp)
with open('anime_dict.pkl', 'wb') as fp:
    pickle.dump(anime_dict, fp)
with open('tags_dict.pkl', 'wb') as fp:
    pickle.dump(tags_dict, fp)
