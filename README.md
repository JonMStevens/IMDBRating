# IMDBRating

Python script that gets info about TV episodes from IMDb and lists that info in a CSV. This information includes the season number, episode number, air date, title, average rating on IMDb, and the number of ratings the episode recieved. This file can then be input into a spreadsheet program and allow you to see trends, high points, and low points in fan reception of a particular series.

usage: ```imdbrating.py [-h] (-url imdb_url | -code imdb_code) csv_file```

The imdb_url parameter should be the URL from either the main show page or the page of a specific season of a TV show on IDMb. The URL will contain a code as described below.

The idmb_code parameter can be used directly instead of a URL. The code will resemble this example: tt0197159. It can be found in the url on the main page or season page of a TV show. It will contain two lower-case t's followed by some (about seven) digits.
Note: If you try and input either the code for a specific episode of a show or the code for a movie then the script will get a 404 error and not work.

The last parameter (example.csv) takes a file name. The file name must use the csv extension.
The script will rewrite an existing csv, or create a new csv if one does not exist with that filename.
