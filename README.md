# IMDBRating
Python script that gets info about TV episodes from IMDb and lists that info in a CSV.
Running the script from the command line will look something like:
>python imdbrating.py tt0197159 example.csv

The first parameter (tt0197159) is a code associated with a show on IMDb. It can be found in the url on the main page of a TV show. It will contain two lower-case t's followed by some (about seven) digits.
If you try and input either the code for a specific episode of a show or the code for a movie then the script will get a 404 error and not work.

The second parameter (example.csv) takes a file name. The file name must use the csv extension.
The script will rewrite an existing csv, or create a new csv if one does not exist with that filename.
