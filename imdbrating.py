"""script for retrieving imdb stats for a tv show on imdb, and writing to csv.
Call static method get_imdb_info_for_show,
pass in an imdb code (found in url) and write returned string to file
"""
# speed up
# could add some brief search feature?
# this might be a good opportunity for async. do multiple seasons at once

from os import error
import sys
import urllib.request
import urllib.parse
import re
import argparse
from bs4 import BeautifulSoup

class IMDBInfoGrabber:
    """class used for retrieving csv info.
    Main method is get_imdb_info_for_show
    """
    @staticmethod
    def get_imdb_info_for_show(imdb_title_id):
        """Returns info to write to csv

        arguments:
        imdb_title_id (string) -- code associated with a show on IMDb.
        Can be found in the url for the show.
        Looks like two lowercase t's followed by digits

        returns:
        string -- csv contents
        """
        print(imdb_title_id)
        print("Working on Season 1")
        csv_text = "Season,Episode,Air Date,Title,Rating,Rating Count\n"

        season_html = IMDBInfoGrabber.__get_season_html(imdb_title_id, 1)
        soup  = BeautifulSoup(season_html, features="html.parser")
        season_count = IMDBInfoGrabber.__get_season_count(soup)
        csv_text += IMDBInfoGrabber.__get_episode_info_for_season(
            soup, 1)

        for i in range(2, season_count + 1):
            print("Working on Season " + str(i))
            season_html = IMDBInfoGrabber.__get_season_html(imdb_title_id, i)
            soup  = BeautifulSoup(season_html, features="html.parser")
            csv_text += IMDBInfoGrabber.__get_episode_info_for_season(
                soup, i)

        print("OK")
        return csv_text.strip()

    @staticmethod
    def __get_episode_info_for_season(soup: BeautifulSoup, season_number: int) -> str:
        """Helper function that gets stats for each episode of a season

        arguments
        html (string) -- html from the page of a season
        season_number (string or int) -- nth season

        return:
        string -- episode stats. stats separated by commas, each episode separated by newline
        """
        episode_blocks = soup.find_all("div", class_="info")
        if not episode_blocks:
            raise error(
                "Could not find episodes for this show. This script may need fixing")

        csv_lines = []

        for episode_block in episode_blocks:
            episode_number_element = episode_block.find("meta", itemprop="episodeNumber")
            episode_number = episode_number_element['content']

            air_date_element = episode_block.find("div", class_="airdate")
            air_date = "" if not air_date_element else air_date_element.text

            title_element = episode_block.find("a", itemprop="name")
            title = "" if not title_element else title_element.text

            rating_element = episode_block.find('span', class_="ipl-rating-star__rating")
            rating = "" if not rating_element else rating_element.text

            rate_count_element = episode_block.find('span', class_="ipl-rating-star__total-votes")
            rate_count = "" if not rate_count_element else rate_count_element.text

            air_date  = air_date.strip("['\\n\t ")
            title = '"' + title.replace("\\'", "'") + '"'
            rate_count = rate_count.strip("()").replace(",","")

            line = (str(season_number) + "," +
            episode_number + "," +
            air_date + "," +
            title + "," +
            rating + "," +
            rate_count)
            csv_lines.append(line)

        return "\n".join(csv_lines) + "\n"

    @staticmethod
    def __get_season_html(imdb_title_id, season_number):
        """helper function that retrieves html for a season of a show

        arguments:
        imdb_title_id (string) -- imdb title id code
        season_number (string or int) -- nth season

        return:
        string -- html
        """
        try:
            with urllib.request.urlopen("https://www.imdb.com/title/"
            f"{imdb_title_id}/episodes?season={season_number}") as response:
                return str(response.read())
        except error as e:
            raise ValueError(
                "A season page could not be found using the given IMDb Title ID") from e
    @staticmethod
    def __get_season_count(soup):
        """helper function that returns number of seasons that a show has

        arguments:
        soup (bs4.BeautifulSoup) -- BeautifulSoup object made from html from the page of a season,
                                    usually the first.

        return:
        int -- season count
        """
        try:
            return len(soup.find('select', id="bySeason").findChildren('option'))
        except AttributeError as e:
            raise ValueError(
                "Could not find number of seasons in given HTML."
                " This script may need fixing") from e

def imdb_code_type(code_str):
    """argument type checker for imdb code str"""
    if not isinstance(code_str, str):
        raise argparse.ArgumentTypeError("IMDb Code was not type string")
    if code_str == "":
        raise argparse.ArgumentTypeError("IMDb Code was empty string")
    if re.fullmatch(r"^tt\d+$", code_str) is None:
        raise argparse.ArgumentTypeError(f"IMDb Code '{code_str}' did not match expected format")
    return code_str
def imdb_url_type(url):
    """argument type checker for imdb url str"""

    if not isinstance(url, str):
        raise argparse.ArgumentTypeError("URL was not type string")
    if url == "":
        raise argparse.ArgumentTypeError("URL was empty string")
    imdb_code_re = re.compile(r"tt\d+(/|$)")
    try:
        parsed_url = urllib.parse.urlparse(url)
        if parsed_url.scheme not in ["http", "https"]:
            raise AttributeError("URL does not have http or https scheme")
        if ".imdb." not in parsed_url.netloc:
            raise AttributeError("URL was not from IMDb")
        imdb_code = imdb_code_re.search(parsed_url.path).group().rstrip("/")
    except AttributeError as e:
        raise argparse.ArgumentTypeError(f"Could not find imdb code with given URL '{url}'."
        " URL must be from a TV show or TV season page on IMDb."
        ) from e
    return imdb_code_type(imdb_code)
def csv_file_type(path_str):
    """argument type checker for csv file name"""
    if not isinstance(path_str, str):
        raise argparse.ArgumentTypeError("CSV file name parameter was not a string")
    if path_str == "":
        raise argparse.ArgumentTypeError("CSV file name parameter was empty string")
    if re.match(r"^[\w,\s-]+\.csv$", path_str) is None:
        raise argparse.ArgumentTypeError("CSV file name parameter "
        f"'{path_str}' not in the correct format. "
        "It should be something like example.csv")
    try:
        return open(path_str, "w", encoding="utf-8")
    except OSError as os_error:

        raise argparse.ArgumentTypeError("CSV file could not be opened using file name:"
        f" '{path_str}'") from os_error

def __main__():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-url",
        type=imdb_url_type,
        nargs=1,
        metavar="imdb_url",
        help="url of a show on imdb.")
    group.add_argument("-code",
        type=imdb_code_type,
        nargs=1, metavar="imdb_code",
        help="Code associated with a show on IMDb found in the url on the main page."
        " It will contain two lower-case t's followed by some (about seven) digits.")
    parser.add_argument("csv_file", type=csv_file_type,
        help="File name with a .csv extension."
        " If this file already exists it will be overwitten.")
    args = parser.parse_args()

    code = (args.url or args.code)[0]
    try:
        with args.csv_file as csv:
            csv.write(IMDBInfoGrabber.get_imdb_info_for_show(code))
    except error:
        print(sys.exc_info()[1])

__main__()
