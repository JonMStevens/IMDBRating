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
import re


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
        if not isinstance(imdb_title_id, str):
            raise TypeError("IMDb Code was not type string")
        if imdb_title_id == "":
            raise ValueError("IMDb Code was empty string")
        if re.fullmatch(r"^tt\d+$", imdb_title_id) is None:
            raise ValueError("IMDb Code did not match expected format")

        print(imdb_title_id)
        print("Working on Season 1")
        csv_text = "Season,Episode,Air Date,Title,Rating,Rating Count\n"

        season_html = IMDBInfoGrabber.__get_season_html(imdb_title_id, 1)
        season__count = IMDBInfoGrabber.__get_season_count(season_html)
        csv_text += IMDBInfoGrabber.__get_episode_info_for_season(
            season_html, 1)

        for i in range(2, season__count + 1):
            print("Working on Season " + str(i))
            season_html = IMDBInfoGrabber.__get_season_html(imdb_title_id, i)
            csv_text += IMDBInfoGrabber.__get_episode_info_for_season(
                season_html, i)

        print("OK")
        return csv_text.strip()

    @staticmethod
    def __get_episode_info_for_season(html, season_number):
        """Helper function that gets stats for each episode of a season

        arguments
        html (string) -- html from the page of a season
        season_number (string or int) -- nth season

        return:
        string -- episode stats. stats separated by commas, each episode separated by newline
        """
        # todo could this be sped up by using find inside the block instead of regex?
        episode_block_re = re.compile(
            r"<div class=\"info\" itemprop=\"episodes\".*?"
            r"</div>.*?ipl-rating-star__total-votes.*?</span>", re.DOTALL)
        episode_number_re = re.compile(r"(?<=episodeNumber\" content=\")\d+")
        air_date_re = re.compile(
            r"(?<=airdate\">..            )\d{1,2} [A-Z][a-z]{2}\.? \d{2,4}")
        title_re = re.compile(r"(?<=title=\").*\" itemprop")
        rating_re = re.compile(r"(?<=ipl-rating-star__rating\">)\d\.\d")
        rate_count = re.compile(
            r"(?<=ipl-rating-star__total-votes\">\()(\d{1,3},)*?\d{1,3}\)")
        csv_lines = []
        episode_info_blocks_html = episode_block_re.findall(html)

        if len(episode_info_blocks_html) == 0:
            raise error(
                "Could not find episodes for this show. This script may need fixing")

        for block in episode_info_blocks_html:
            line = str(season_number) + ","
            line += episode_number_re.search(block).group() + ","
            line += air_date_re.search(block).group() + ","
            line += "\"" + \
                title_re.search(block).group().rstrip(
                    " itemprop").replace("\\'", "'") + ","
            line += rating_re.search(block).group() + ","
            line += rate_count.search(block).group().replace(",",
                                                            "").rstrip(")")
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
    def __get_season_count(html):
        """helper function that returns number of seasons that a show has

        arguments:
        html (string) -- html from the page of a season, usually the first.

        return:
        int -- season count
        """
        try:
            season_dropdown_html = re.search(
                "<select id=\"bySeason\".*?</select>", html).group()
        except error as e:
            raise error(
                "Could not find number of seasons in given HTML."
                " This script may need fixing") from e

        return len(re.findall("<option.*?</option>", season_dropdown_html))


def __main__():
    if len(sys.argv) != 3:
        print("Missing Arguments")
        return
    if not isinstance(sys.argv[2], str):
        print("CSV file name parameter was not a string")
        return
    if sys.argv[2] == "":
        print("CSV file name parameter was empty string")
        return
    if re.match(r"^[\w,\s-]+\.csv$", sys.argv[2]) is None:
        print("CSV file name parameter not in the correct format."
        " It should be something like example.csv")
        return

    try:
        with open(sys.argv[2], "w", encoding="utf-8") as csv:
            csv.write(IMDBInfoGrabber.get_imdb_info_for_show(
                sys.argv[1]))
    except error:
        print(sys.exc_info()[1])


__main__()
