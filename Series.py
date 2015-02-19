#!/usr/bin/python
import sys
import urllib2
from imdb import IMDb
from bs4 import BeautifulSoup
from os.path import expanduser, join
import re

EPISODE_MARKER = "*** "
SEASON_MARKER = "** SEASON"
SHOW_MARKER = "* "
MAPFILE_LOCATION = join(expanduser("~"), ".show_tracker", "title_imdbId.map")

class Show:
    def __init__(self, titleLine):
        self.title = titleLine[len(SHOW_MARKER):]
        self.seasons = dict()

    def addSeason(self, seasonNumber):
        if not seasonNumber in self.seasons:
            self.seasons[seasonNumber] = Season(seasonNumber)

    def addEpisode(self, seasonNumber, episodeNumber, episodeTitle, episodeStatus):
        self.addSeason(seasonNumber)
        self.seasons[seasonNumber].addEpisode(episodeNumber, episodeTitle, episodeStatus)

    def update(self, imdbAccess, showId):
        url = "http://www.imdb.com/title/tt" + showId + "/epdate"
        unparsed = BeautifulSoup(urllib2.urlopen(url).read())
        episodesTable = BeautifulSoup(unparsed.find_all("table")[0].encode("utf-8"))
        episodes = episodesTable.find_all("tr")[1:]
        for episode in episodes:
            tds = episode.find_all("td")
            series_and_episode =  tds[0].string
            if series_and_episode.startswith("-"):
                continue
            series = series_and_episode.split(".")[0]
            episode = series_and_episode.split(".")[1]
            title = tds[1].a.string
            rating = tds[2].string
            self.addEpisode(int(series), int(episode), title, 'UNWATCHED')

    def __unicode__(self):
        returnValue = SHOW_MARKER + self.title + "\n"
        for no, serie in sorted(self.seasons.iteritems(), key=lambda season: season[1].number):
            returnValue += unicode(serie)

        return returnValue

class Season:
    def __init__(self, seasonNumer):
        self.number = int(seasonNumer)
        self.episodes = dict()

    def addEpisode(self, episodeNumber, episodeTitle, episodeStatus):
        if not episodeNumber in self.episodes:
               self.episodes[episodeNumber] = Episode(self.number, episodeNumber, episodeTitle, episodeStatus)

    def __unicode__(self):
        returnValue =  SEASON_MARKER + " " + str(self.number).encode("utf-8").zfill(2) + "\n"
        for no, episode in sorted(self.episodes.iteritems(), key=lambda episode: episode[1].number):
            returnValue += unicode(episode)

        return returnValue


class Episode:
    def __init__(self, series, numberInSeries, title, status):
        self.seriesNumber = series
        self.title = title
        self.number = int(numberInSeries)
        self.status = status

    def __unicode__(self):
        return self.__repr__()

    def __repr__(self):
        return unicode(EPISODE_MARKER) + u"S" + unicode(self.seriesNumber).zfill(2) + u"E" + unicode(self.number).zfill(2) + u' "' + self.title + u"\" " + unicode(self.status) + u"\n"

class ShowTracker:
    def __init__(self, dataFile):
        self.imdbAccess = IMDb()
        self.dataFileName = dataFile
        self.series = []
        self.offsets = {}
        self.readDataFiles()
        self.fillSeriesMap()
        self.updateShows()
        self.saveShows()

    def saveShows(self):
        for show in self.series:
            print unicode(show).encode('utf-8')

    def updateShows(self):
        for show in self.series:
            show.update(self.imdbAccess, self.map[show.title])

    def readDataFiles(self):
        seriesProgressFile = open(self.dataFileName, 'r+')
        currentShow = None
        for line in seriesProgressFile:
            line = line.rstrip("\n")
            if line.startswith(EPISODE_MARKER):
                match = re.match('.*S(?P<seasonNo>.*?)E(?P<episodeNo>.+?)\s*"(?P<title>.+?)"\s*(?P<status>.*)', line)
                currentShow.addEpisode(int(match.group('seasonNo')), int(match.group('episodeNo')), match.group('title').decode("utf-8"), match.group('status'))
                pass
            elif line.startswith(SEASON_MARKER):
                currentShow.addSeason(int(line[len(SEASON_MARKER):]))
            elif line.startswith(SHOW_MARKER):
                if currentShow is not None:
                    self.series.append(currentShow)
                currentShow = Show(line)
        if currentShow is not None:
            self.series.append(currentShow)
        seriesProgressFile.close()
        self.map = dict()
        mapFile = open(MAPFILE_LOCATION, 'r')
        for line in mapFile:
            mapping = line.rstrip("\n").split("^")
            self.map[mapping[0]] = mapping[1]
        mapFile.close()

    def fillSeriesMap(self):
        for tvSerie in self.series:
            if not tvSerie.title in self.map:
                self.map[tvSerie.title] = self.getShowId(tvSerie.title)

        mapFile = open(MAPFILE_LOCATION, 'w')
        for title, id in self.map.iteritems():
            mapFile.write(title + "^" + id + "\n")

    def getShowId(self, title):
        candidates = self.imdbAccess.search_movie(title)
        candidates = [tvSerie for tvSerie in candidates if tvSerie['kind'] == 'tv series']
        i = 0
        if len(candidates) == 1:
            pass
        else:
            for cd in candidates:
                i += 1
                print str(i) + ")" + cd.summary()

            print "Dear sir, can you point which series is on your mind?"
            choice = int(raw_input("My choice is: "))
            i -= 1
        return self.imdbAccess.get_imdbID(candidates[0])



if __name__ == "__main__":
    s = ShowTracker(sys.argv[1])
