# speed up
# could add some brief search feature?
# this might be a good opportunity for async. do multiple seasons at once

from os import error
import sys
import urllib.request
import re


class IMDBInfoGrabber:
    @staticmethod
    def GetIMDBInfoForShow(imdbTitleID):
        if type(imdbTitleID) != type("a string"):
            raise TypeError("IMDb Code was not type string")
        if imdbTitleID == "":
            raise ValueError("IMDb Code was empty string")
        if re.fullmatch("^tt\d+$", imdbTitleID) is None:
            raise ValueError("IMDb Code did not match expected format")

        print(imdbTitleID)
        print("Working on Season 1")
        csvText = "Season,Episode,Air Date,Title,Rating,Rating Count\n"

        seasonHTML = IMDBInfoGrabber.__getSeasonHTML(imdbTitleID, 1)
        seasonCount = IMDBInfoGrabber.__getSeasonCount(seasonHTML)
        csvText += IMDBInfoGrabber.__getEpisodeInfoForSeason(
            seasonHTML, 1)

        for i in range(2, seasonCount + 1):
            print("Working on Season " + str(i))
            seasonHTML = IMDBInfoGrabber.__getSeasonHTML(imdbTitleID, i)
            csvText += IMDBInfoGrabber.__getEpisodeInfoForSeason(
                seasonHTML, i)

        print("OK")
        return csvText.strip()

    def __getEpisodeInfoForSeason(html, seasonNumber):
        # todo could this be sped up by using find inside the block instead of regex?
        episodeBlockRe = re.compile(
            "<div class=\"info\" itemprop=\"episodes\".*?</div>.*?ipl-rating-star__total-votes.*?</span>", re.DOTALL)
        episodeNumberRe = re.compile("(?<=episodeNumber\" content=\")\d+")
        airDateRe = re.compile(
            "(?<=airdate\">..            )\d{1,2} [A-Z][a-z]{2}\.? \d{2,4}")
        titleRe = re.compile("(?<=title=\").*\" itemprop")
        ratingRe = re.compile("(?<=ipl-rating-star__rating\">)\d\.\d")
        rateCount = re.compile(
            "(?<=ipl-rating-star__total-votes\">\()(\d{1,3},)*?\d{1,3}\)")
        csvLines = []
        episodeInfoBlocksHTML = episodeBlockRe.findall(html)

        if (len(episodeInfoBlocksHTML) == 0):
            raise error(
                "Could not find episodes for this show. This script may need fixing")

        for block in episodeInfoBlocksHTML:
            line = str(seasonNumber) + ","
            line += episodeNumberRe.search(block).group() + ","
            line += airDateRe.search(block).group() + ","
            line += "\"" + \
                titleRe.search(block).group().rstrip(
                    " itemprop").replace("\\'", "'") + ","
            line += ratingRe.search(block).group() + ","
            line += rateCount.search(block).group().replace(",",
                                                            "").rstrip(")")
            csvLines.append(line)

        return "\n".join(csvLines) + "\n"

    def __getSeasonHTML(imdbTitleID, seasonNumber):
        try:
            with urllib.request.urlopen(f"https://www.imdb.com/title/{imdbTitleID}/episodes?season={seasonNumber}") as response:
                return str(response.read())
        except:
            raise ValueError(
                "A season page could not be found using the given IMDb Title ID")

    def __getSeasonCount(html):
        try:
            seasonDropdownHTML = re.search(
                "<select id=\"bySeason\".*?</select>", html).group()
        except:
            raise error(
                "Could not find number of seasons in given HTML. This script may need fixing")

        return len(re.findall("<option.*?</option>", seasonDropdownHTML))


def __main__():
    if len(sys.argv) != 3:
        print("Missing Arguments")
        return
    if type(sys.argv[2]) != type("a string"):
        print("CSV file name parameter was not a string")
        return
    if sys.argv[2] == "":
        print("CSV file name parameter was empty string")
        return
    if re.match("^[\w,\s-]+\.csv$", sys.argv[2]) is None:
        print("CSV file name parameter not in the correct format. It should be something like example.csv")
        return

    try:
        with open(sys.argv[2], "w") as csv:
            csv.write(IMDBInfoGrabber.GetIMDBInfoForShow(
                sys.argv[1]))
    except:
        print(sys.exc_info()[1])


__main__()
