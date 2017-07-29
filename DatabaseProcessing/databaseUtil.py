import math

from DatabaseProcessing import sqlUtil
from Players.AIPlayers.TakNet2.Train import boardSize

databaseLocation = "Database"
rawDatabaseSubFolder = databaseLocation + "/Raw"
boardSizeSubFolder = databaseLocation + "/Board_Size_" + str(boardSize)
filteredDatabaseSubFolder = boardSizeSubFolder + "/Filtered"
parsedGameStatesSubFolder = boardSizeSubFolder + "/ParsedGameStates"
permutedGameStatesSubFolder = boardSizeSubFolder + "/PermutedGameStates"

sqlFilterFileName = rawDatabaseSubFolder + "/size_and_non_resign_filter"
moveCountFilterFileName = rawDatabaseSubFolder + "/count_moves_filter"
gameCountFilterFileName = rawDatabaseSubFolder + "/count_games_filter"

rawDatabaseFilename = rawDatabaseSubFolder + "games_anon_7_29_17.db"
filteredDatabaseFilename = filteredDatabaseSubFolder + "/filteredGames"
parsedGamesStatesBaseFilename = parsedGameStatesSubFolder + "/parsedGameStates_"
permutedGameStatesBaseFilename = permutedGameStatesSubFolder + "/permutedGameStates_"

numberOfGames = sqlUtil.countGames()
gamesPerParseFile = 10000
numberOfParseFiles = int(math.ceil(numberOfGames / gamesPerParseFile))
parsePermuteRatio = 10
gamesPerPermuteFile = gamesPerParseFile // parsePermuteRatio
numberOfPermuteFiles = numberOfParseFiles * gamesPerParseFile // gamesPerPermuteFile


def getNumberOfExamplesInDatabase():
    # includes permutations
    return sqlUtil.countMoves() * 16


def filterDatabase():
    # todo
    raise NotImplementedError


def parseDatabase():
    # todo
    raise NotImplementedError
