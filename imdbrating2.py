# todo elim need for 2nd param

import sys
import urllib.request
import re


class IMDBInfoGrabber:
    @staticmethod
    def GetIMDBInfoForShow(imdbTitleID, seasonCount):
        if type(imdbTitleID) != type("a string"):
            print("IMDb Code was not type string")
            return ""
        if type(seasonCount) != type(1):
            print("Season Count was not type int")
            return ""
        if imdbTitleID == "":
            print("IMDb Code was empty string")
            return ""
        if seasonCount < 0:
            print("Season Count was less than 1")
            return ""
        if re.fullmatch("^tt\d+$", imdbTitleID) is None:
            print("IMDb Code did not match expected format")
            return ""

        print(imdbTitleID)
        ret = "Season,Episode,Air Date,Title,Rating,Rating Count\n"
        for i in range(1, seasonCount + 1):
            print("Working on Season " + str(i))
            ret += IMDBInfoGrabber.__getEpisodeInfoForSeason(
                imdbTitleID, i) + "\n"

        print("OK")
        return ret.strip()

    def __getEpisodeInfoForSeason(imdbTitleID, seasonNumber):
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
        # todo give better message if url does not work
        with urllib.request.urlopen(f"https://www.imdb.com/title/{imdbTitleID}/episodes?season={seasonNumber}") as response:
            html = str(response.read())
            episodeInfoBlocks = episodeBlockRe.findall(html)

            for block in episodeInfoBlocks:
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
        return "\n".join(csvLines)


def __main__():
    if len(sys.argv) < 4:
        print("Missing Arguments")
        return

    try:
        seasonCount = int(sys.argv[2])
    except:
        print("Invalid Season Count: " + sys.argv[2])
        return

    try:
        with open(sys.argv[3], "w") as csv:
            csv.write(IMDBInfoGrabber.GetIMDBInfoForShow(
                sys.argv[1], seasonCount))
    except:
        print(sys.exc_info()[1])


__main__()
