# speed up
# could add some brief search feature?
# this might be a good opportunity for async. do multiple seasons at once

import sys
import urllib.request
import re


class IMDBInfoGrabber:
    @staticmethod
    def GetIMDBInfoForShow(imdbTitleID):
        if type(imdbTitleID) != type("a string"):
            print("IMDb Code was not type string")
            return ""
        if imdbTitleID == "":
            print("IMDb Code was empty string")
            return ""
        if re.fullmatch("^tt\d+$", imdbTitleID) is None:
            print("IMDb Code did not match expected format")
            return ""

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
        # todo give better message if url does not work
        with urllib.request.urlopen(f"https://www.imdb.com/title/{imdbTitleID}/episodes?season={seasonNumber}") as response:
            return str(response.read())
    def __getSeasonCount(html):
        seasonDropdownHTML = re.search("<select id=\"bySeason\".*?</select>", html).group()
        return len(re.findall("<option.*?</option>", seasonDropdownHTML))

def __main__():
    if len(sys.argv) < 3:
        print("Missing Arguments")
        return
    
    # todo put more requirement on filenames
    # todo give better message if this does not work
    try:
        with open(sys.argv[2], "w") as csv:
            csv.write(IMDBInfoGrabber.GetIMDBInfoForShow(
                sys.argv[1]))
    except:
        print(sys.exc_info()[1])


__main__()
