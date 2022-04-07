"""script for retrieving imdb stats for a tv show on imdb, and writing to csv.
Call static method get_imdb_info_for_show,
pass in an imdb code (found in url) and write returned string to file
"""
#todo: add types to functions
#todo: move unit tests
# speed up
# could add some brief search feature?
# this might be a good opportunity for async. do multiple seasons at once

from io import TextIOWrapper
from os import error
import sys
import urllib.request
import urllib.parse
import re
import argparse
import unittest
from bs4 import BeautifulSoup

class TestIMDBInfoGrabber(unittest.TestCase):
    """tests IMDBInfoGrabber.get_imdb_info_for_show"""
    def test_happy(self):
        """happy path test
        imdb code for Home Movies"""
        self.assertIsInstance(IMDBInfoGrabber.get_imdb_info_for_show("tt0197159"), str)
        self.assertNotEqual(IMDBInfoGrabber.get_imdb_info_for_show("tt0197159"), "")
    def test_movie(self):
        """test imdb code of movie
        imdb code for Sleeping Beauty"""
        with self.assertRaises(ValueError):
            IMDBInfoGrabber.get_imdb_info_for_show("tt0053285")
    def test_episode(self):
        """test imdb code of episode
        imdb code for futurama: luck of the fryish"""
        with self.assertRaises(ValueError):
            IMDBInfoGrabber.get_imdb_info_for_show("tt0768678")
    def test_nothing_code(self):
        """test valid imdb code that points to nothing"""
        with self.assertRaises(ValueError):
            IMDBInfoGrabber.get_imdb_info_for_show("tt0000000")
    def test_bad_code(self):
        """test invalid imdb code"""
        with self.assertRaises(ValueError):
            IMDBInfoGrabber.get_imdb_info_for_show("tt12")
        with self.assertRaises(ValueError):
            IMDBInfoGrabber.get_imdb_info_for_show("tt1212121212121212")
    def test_non_code_string(self):
        """test a string that is not a code"""
        with self.assertRaises(ValueError):
            IMDBInfoGrabber.get_imdb_info_for_show("t")
    def test_non_code_empty_string(self):
        """test empty string that is not a code"""
        with self.assertRaises(ValueError):
            IMDBInfoGrabber.get_imdb_info_for_show("")
    def test_non_code_string_class(self):
        """test passing string class"""
        #todo: converts to /title/<class 'str'>/episodes?season=1
        # does this: raise InvalidURL(f"URL can't contain control characters. {url!r} "
        with self.assertRaises(ValueError):
            IMDBInfoGrabber.get_imdb_info_for_show(str)
    def test_non_code_int(self):
        """test an int that is not a code"""
        with self.assertRaises(ValueError):
            IMDBInfoGrabber.get_imdb_info_for_show(0)
    def test_non_code_float(self):
        """test a float that is not a code"""
        with self.assertRaises(ValueError):
            IMDBInfoGrabber.get_imdb_info_for_show(1.2)
class TestParseArgs(unittest.TestCase):
    """tests parse_args"""
    @staticmethod
    def has_all_attr(args: argparse.Namespace) -> bool:
        """helper function to test that all args exist in namespace"""
        return hasattr(args, "url") and hasattr(args, "code") and hasattr (args, "csv_file")
    def test_happy_with_code(self):
        """happy path test with code as arg
        imdb code for Home Movies"""
        argv = ["-code", "tt0197159", "homemovies.csv"]
        args = parse_args(argv)
        self.assertIsInstance(args, argparse.Namespace)
        self.assertTrue(TestParseArgs.has_all_attr(args))
        self.assertIsNone(args.url)
        self.assertEqual(args.code, ["tt0197159"])
        self.assertIsInstance(args.csv_file, TextIOWrapper)
        args.csv_file.close()

    def test_happy_with_url_episode_list(self):
        """happy path test with url as arg
        url goes to episode list
        code is for star trek deep space 9"""
        argv = ["-url", "https://www.imdb.com/title/tt0106145/episodes?season=1", "ds9.csv"]
        args = parse_args(argv)
        self.assertIsInstance(args, argparse.Namespace)
        self.assertTrue(TestParseArgs.has_all_attr(args))
        self.assertIsNone(args.code)
        self.assertEqual(args.url, ["tt0106145"])
        self.assertIsInstance(args.csv_file, TextIOWrapper)
        args.csv_file.close()
    def test_happy_with_url(self):
        """happy path test with url as arg
        code is for star trek deep space 9"""
        argv = ["-url", "https://www.imdb.com/title/tt0106145/", "ds9.csv"]
        args = parse_args(argv)
        self.assertIsInstance(args, argparse.Namespace)
        self.assertTrue(TestParseArgs.has_all_attr(args))
        self.assertIsNone(args.code)
        self.assertEqual(args.url, ["tt0106145"])
        self.assertIsInstance(args.csv_file, TextIOWrapper)
        args.csv_file.close()
    def test_happy_with_url_no_trailing_slash(self):
        """happy path test with url as arg
        url has no traling /
        code is for star trek deep space 9"""
        argv = ["-url", "https://www.imdb.com/title/tt0106145", "ds9.csv"]
        args = parse_args(argv)
        self.assertIsInstance(args, argparse.Namespace)
        self.assertTrue(TestParseArgs.has_all_attr(args))
        self.assertIsNone(args.code)
        self.assertEqual(args.url, ["tt0106145"])
        self.assertIsInstance(args.csv_file, TextIOWrapper)
        args.csv_file.close()
    def test_happy_with_url_with_ref(self):
        """happy path test with url as arg with a ?ref in url
        code is for fridays"""
        argv = ["-url", "https://www.imdb.com/title/tt0080219/?ref_=nm_flmg_wr_14", "fridays.csv"]
        args = parse_args(argv)
        self.assertIsInstance(args, argparse.Namespace)
        self.assertTrue(TestParseArgs.has_all_attr(args))
        self.assertIsNone(args.code)
        self.assertEqual(args.url, ["tt0080219"])
        self.assertIsInstance(args.csv_file, TextIOWrapper)
        args.csv_file.close()
    def test_double_dashes(self):
        """test with double dashes in front of arg flag, should reject"""
        argv = ["--code", "tt0197159", "homemovies.csv"]
        with self.assertRaises(SystemExit):
            parse_args(argv)

    def test_csv_arg_flag(self):
        """test with arg flag for csv arg, should reject"""
        argv = ["-code", "tt0197159", "-csv", "homemovies.csv"]
        with self.assertRaises(SystemExit):
            parse_args(argv)

    def test_non_imdb_url(self):
        """test url that is not an imdb site, should reject"""
        argv = ["-url",
        ("https://stackoverflow.com/questions/827557/"
        "how-do-you-validate-a-url-with-a-regular-expression-in-python"),
        "ds9.csv"]
        with self.assertRaises(SystemExit):
            parse_args(argv)

    def test_non_url(self):
        """test url that goes nowhere, should reject"""
        argv = ["-url", "https://alfjalafafghagla.zzz/", "ds9.csv"]
        with self.assertRaises(SystemExit):
            parse_args(argv)

    def test_only_csv(self):
        """test argv only has csv argument, missing code or url"""
        argv = ["homemovies.csv"]
        with self.assertRaises(SystemExit):
            parse_args(argv)

    def test_only_code(self):
        """test argv only has csv argument, missing code or url"""
        argv = ["tt0197159"]
        with self.assertRaises(SystemExit):
            parse_args(argv)

    def test_only_flag(self):
        """test argv only has csv argument, missing code or url"""
        argv = ["-code"]
        with self.assertRaises(SystemExit):
            parse_args(argv)

    def test_missing_arg_flag(self):
        """test argv is missing -url or -code flag"""
        argv = ["tt0197159", "homemovies.csv"]
        with self.assertRaises(SystemExit):
            parse_args(argv)

    def test_empty_code(self):
        """test empty string as code arg"""
        argv = ["-code", "", "homemovies.csv"]
        with self.assertRaises(SystemExit):
            parse_args(argv)

    def test_empty_csv(self):
        """test empty string as csv arg"""
        argv = ["-code", "tt0197159", ""]
        with self.assertRaises(SystemExit):
            parse_args(argv)

    def test_nameless_csv(self):
        """test .csv csv arg"""
        argv = ["-code", "tt0197159", ".csv"]
        with self.assertRaises(SystemExit):
            parse_args(argv)

    def test_short_code(self):
        """test invalid imdb code that is too short"""
        argv = ["-code", "tt12", ".csv"]
        with self.assertRaises(SystemExit):
            parse_args(argv)

    def test_long_code(self):
        """test invalid imdb code that is too long"""
        argv = ["-code", "tt122112112211212", ".csv"]
        with self.assertRaises(SystemExit):
            parse_args(argv)

    def test_non_code(self):
        """test a string that is not a code"""
        argv = ["-code", "t", "homemovies.csv"]
        with self.assertRaises(SystemExit):
            parse_args(argv)

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

def parse_args(argv: list) -> argparse.Namespace:
    """returns Namespace of args including:
    args.url
    args.code
    args.csv_file"""
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
    return parser.parse_args(argv)

def __main__():
    args = parse_args(sys.argv[1:])
    code = (args.url or args.code)[0]
    try:
        with args.csv_file as csv:
            csv.write(IMDBInfoGrabber.get_imdb_info_for_show(code))
    except error:
        print(sys.exc_info()[1])

__main__()
