AniDB Tag Miner
---------------

Simple script for extracting AniDB title information from downloaded Season Chart HTML pages.

Example URL that you need to download and place into a folder named `htmls/` that should be created adjacent to the Python file `anidb.py`:

`https://anidb.net/perl-bin/animedb.pl?show=calendar`

The script loops through HTML files and their HTML elements and extract information such as the anime's title, date, ratings, tags.

Output is a JSON file named `extracted_data.json`.

You must have the `BeautifulSoup4` module installed.
