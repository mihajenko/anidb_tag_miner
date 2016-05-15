#!/usr/bin/env python

import json
import pickle
import sys
from collections import Counter
from operator import itemgetter
from pprint import PrettyPrinter
import random

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import AgglomerativeClustering
from sklearn.cluster import KMeans


def output_orange_tab_file(anime_dict):
    if not anime_dict:
        return

    print('Writing similarity matrix to Orange tab format')
    print()
    feature_names = [t[0] for t in sorted(anime_dict.items(),
                     key=itemgetter(1))]
    first_row = '\t'.join(feature_names)
    second_row = '\t'.join(['c'] * len(feature_names))
    third_row = '\t'.join([''] * len(feature_names))
    data_rows = ''

    anime_n = len(anime_dict)
    anime_i = 0
    for x in np.nditer(sim_mat):
        if anime_i == anime_n:
            data_rows = data_rows[:-1] + '\n'
            anime_i = 0
        else:
            data_rows += '{0}\t'.format(x)
            anime_i += 1

    file_data = '{0}\n{1}\n{2}\n{3}'.format(first_row, second_row, third_row,
                                            data_rows)
    with open('orange.tab', 'w') as fp:
        fp.write(file_data)

if __name__ == '__main__':
    """
    Reffer to README.md for instructions.
    """

    # for debugging
    pprint = PrettyPrinter(indent=2).pprint

    # check for JSON filename in arguments, or default to 'extracted_data.json'
    try:
        js_name = sys.argv[1]
    except IndexError:
        js_name = 'extracted_data.json'

    # open JSON file
    with open(js_name, 'r') as f:
        data = json.load(f)

    # get total anime titles and total tags, build a tag reference dict
    anime_n = 0
    tag_n = 0
    # for tag name lookup for tag info
    tags_dict = {}
    # for index (reverse) lookup for tag name
    tagsr_dict = {}
    for year, v in data.items():
        for season, anime in v.items():
            for an in anime:
                # check if complete data
                try:
                    float(an['rating']['mean']['value'])
                    float(an['rating']['mean']['count'])
                except ValueError:
                    continue
                # count another anime
                anime_n += 1

                tags = an['tags']
                for tag in tags:
                    try:
                        name = tags_dict[tag['tag']]
                    except KeyError:
                        tags_dict[tag['tag']] = [tag_n, tag['description']]
                        tagsr_dict[tag_n] = [tag['tag'], tag['description']]
                        # count another tag
                        tag_n += 1

    # anime-tag count matrix
    at = np.zeros((anime_n, tag_n))
    # compare matrix
    sim_mat = np.zeros((anime_n, anime_n))

    # fill up anime-tag matrix, build a anime reference dict
    anime_dict = {}
    mean_dict = {}
    count_dict = {}
    i = 0
    for year, v in data.items():
        for season, anime in v.items():
            for an in anime:
                # check if complete data
                mean_v = an['rating']['mean']['value']
                mean_c = an['rating']['mean']['count']
                try:
                    mean_dict[i] = float(mean_v)
                    count_dict[i] = float(mean_c)
                except ValueError:
                    continue

                anime_dict[an['title']] = i

                tags = an['tags']
                for tag in tags:
                    at[i, tags_dict[tag['tag']][0]] = 1
                i += 1

    # compare anime vectors with cosine similarity and build similarity matrix
    sim_mat = cosine_similarity(at)
    print('Anime-Tag matrix shape:', at.shape)
    print('Similarity matrix shape:', sim_mat.shape)
    print()

    # save to pickles
    with open('at.pkl', 'wb') as fp:
        pickle.dump(at, fp)
    with open('sim_mat.pkl', 'wb') as fp:
        pickle.dump(sim_mat, fp)
    with open('anime_dict.pkl', 'wb') as fp:
        pickle.dump(anime_dict, fp)
    with open('tags_dict.pkl', 'wb') as fp:
        pickle.dump(tags_dict, fp)

    # write to an orange file
    output_orange_tab_file(anime_dict)

    # clustering - we got 4 clusters with Orange K-Means different metrics
    ac = KMeans(n_clusters=4, precompute_distances=False, max_iter=600,
                tol=1e-5, n_init=20, random_state=23465684, n_jobs=2)
    # returns cluster labels
    clabels = ac.fit_predict(sim_mat)

    # anime items
    anime_items = sorted(anime_dict.items(), key=itemgetter(1))

    for idx, cl in enumerate(clabels):
        anime_items[idx] = list(anime_items[idx]) + [cl, ]

    cluster_means = [[], [], [], [], ]
    cluster_counts = [[], [], [], [], ]
    # calculate cluster means

    for title, idx, cl in anime_items:
        cluster_means[cl].append(mean_dict[idx])
        cluster_counts[cl].append(count_dict[idx])

    print('Cluster means:')
    print('Cluster 0 (mean, cardinality):',
          np.mean(cluster_means[0]), len(cluster_means[0]))
    print('Cluster 1 (mean, cardinality):',
          np.mean(cluster_means[1]), len(cluster_means[1]))
    print('Cluster 2 (mean, cardinality):',
          np.mean(cluster_means[2]), len(cluster_means[2]))
    print('Cluster 3 (mean, cardinality):',
          np.mean(cluster_means[3]), len(cluster_means[3]))

    # calculate cluster counts
    print('Cluster counts:')
    print('Cluster 0 (mean, cardinality):',
          np.mean(cluster_counts[0]), len(cluster_counts[0]))
    print('Cluster 1 (mean, cardinality):',
          np.mean(cluster_counts[1]), len(cluster_counts[1]))
    print('Cluster 2 (mean, cardinality):',
          np.mean(cluster_counts[2]), len(cluster_counts[2]))
    print('Cluster 3 (mean, cardinality):',
          np.mean(cluster_counts[3]), len(cluster_counts[3]))

    # see most common genres
    print()
    for cl_p in range(4):
        cou = Counter()
        for idx, cl in enumerate(clabels):
            if cl == cl_p:
                for jdx, a in enumerate(at[idx, :]):
                    if a == 1:
                        cou[tagsr_dict[jdx][0]] += 1

        print('Top 8 most common genres in cluster', cl_p)
        for tag, cnt in cou.most_common(20):
            print('\t{0} (anime with this tag: {1})'.format(tag, cnt))
        print()
