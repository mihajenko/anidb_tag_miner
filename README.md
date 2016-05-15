AniDB Tag Miner
---------------

A collection of Python tools for extracting information from AniDB's Season Chart HTML web pages and statistical analysis.


### Requirements

Check out `requirements.txt`. If you prefer, use pip to install any dependencies.

**Usage:** `pip install -r requirements.txt`


### Tools

#### anidb_extract.py

Simple script for extracting AniDB title information from downloaded Season Chart HTML pages.

You can download the HTML files from [here](https://anidb.net/perl-bin/animedb.pl?show=calendar). You need to download the HTML files separately and place them into a folder that should be created in the same folder as the Python file. An example folder and an example HTML file are provided for testing.

The script opens HTML files placed in the aforementioned folder and loops through their HTML elements. For each anime it extracts information such as the anime's title, date, ratings, tags and places them into a JSON file. You can provide a second argument to the program, or the output file will be saved as `extracted_data.json`.

**Example usage:** `python anidb_extract.py example_folder example.json`

You must have the `BeautifulSoup4` package installed.

#### stats.py

This script returns a pickled cosine similarity distance matrix from `extracted_data.json`, as well as an anime-tag existence matrix, along with two dicts containing anime and tag index reference numbers for the existence matrix. The returned pickles are named `sim_mat.pkl`, `at.pkl`, `anime_dict.pkl`, `tags_dict.pkl`, respectively. It also clusters these similarity measures and prints results such as cluster means and most common tags for each cluster.

**Example usage:** `python stats.py extracted_data.json`

Both matrices are in dense `numpy.ndarray` format and require the `numpy` package. You will also need `scipy` and `scikit-learn` packages.
