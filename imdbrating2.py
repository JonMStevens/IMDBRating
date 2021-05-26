import urllib.request
import re

class IMDBInfoGrabber:
    @staticmethod
    def GetIMDBInfoForShow(imdbTitleID, seasonCount):
        match = re.search("\d", "a8b")
        if type(imdbTitleID) != type("a string"):
            print("First paramter was not type string")
            return ""
        if type(seasonCount) != type(1):
            print("Second paramter was not type int")
            return ""
        if imdbTitleID == "":
            print("First paramter was empty string")
            return ""
        if seasonCount < 0:
            print("Second paramter was less than 1")
            return ""
        if re.fullmatch("^tt\d+$", imdbTitleID) is None:
            print("First parameter did not match expected format")
            return ""

        print(imdbTitleID)
        ret = ""
        for i in range(1, seasonCount + 1):
            print("Working on Season " + str(i))
            ret += IMDBInfoGrabber.__getEpisodeInfoForSeason(imdbTitleID, i)


        print("OK")
        return ret

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
        with urllib.request.urlopen(f"https://www.imdb.com/title/{imdbTitleID}/episodes?season={seasonNumber}") as response:
            html = str(response.read())
            matches = episodeBlockRe.findall(html)
            for match in matches:
                line = ""
                line += str(seasonNumber) + ","
                line += episodeNumberRe.search(match).group() + ","
                line += airDateRe.search(match).group() + ","
                line += "\"" + \
                    titleRe.search(match).group().rstrip(
                        " itemprop").replace("\\'", "'") + ","
                line += ratingRe.search(match).group() + ","
                line += rateCount.search(match).group().rstrip(")")
                csvLines.append(line)
        return "\n".join(csvLines)


print(IMDBInfoGrabber.GetIMDBInfoForShow("tt0197159", 4))
