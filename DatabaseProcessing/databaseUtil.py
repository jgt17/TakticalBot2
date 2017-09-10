import math

from Players.AIPlayers.TakNet2.config import boardSize

databaseLocation = "Database"
rawDatabaseSubFolder = databaseLocation + "/Raw"
boardSizeSubFolder = databaseLocation + "/Board_Size_" + str(boardSize)
filteredDatabaseSubFolder = boardSizeSubFolder + "/Filtered"
parsedGameStatesSubFolder = boardSizeSubFolder + "/ParsedGameStates"
permutedGameStatesSubFolder = boardSizeSubFolder + "/PermutedGameStates"

sqlFilterFileName = rawDatabaseSubFolder + "/size_and_non_resign_filter"
moveCountFilterFileName = rawDatabaseSubFolder + "/count_moves_filter"
gameCountFilterFileName = rawDatabaseSubFolder + "/count_games_filter"

rawDatabaseFilename = rawDatabaseSubFolder + "/games_anon_7_29_17.db"
filteredDatabaseFilename = filteredDatabaseSubFolder + "/filteredGames"
parsedGamesStatesBaseFilename = parsedGameStatesSubFolder + "/parsedGameStates_"
permutedGameStatesBaseFilename = permutedGameStatesSubFolder + "/permutedGameStates_"

from DatabaseProcessing import sqlUtil

numberOfGames = sqlUtil.countGames(boardSize)
gamesPerParseFile = 10000
numberOfParseFiles = int(math.ceil(numberOfGames / gamesPerParseFile))
parsePermuteRatio = 10
gamesPerPermuteFile = gamesPerParseFile // parsePermuteRatio
numberOfPermuteFiles = numberOfParseFiles * gamesPerParseFile // gamesPerPermuteFile


# count the total number of moves across all games in the database of the appropriate size
def getNumberOfExamplesInDatabase():
    # includes permutations
    return sqlUtil.countMoves(boardSize) * 16


# select the notation and result from games which did not result in a resignation
def filterDatabase():
    return sqlUtil.filterGames(boardSize)


# convert the filtered database to a CSV string
def convertToCSVString(filteredDB):
    with open(filteredDatabaseFilename, "w") as f:
        for game in filteredDB:
            f.write(str(game[0]) + ";" + str(game[1]) + "\n")


# parse gamestates from each game
def parseDatabase():
    from DatabaseProcessing.ParseGameStates import parseGameStates
    parseGameStates()


# permute existing gamestates
def permuteDatabase():
    raise NotImplementedError
    # todo


# prepare database for injest by training algorithm
def processDatabase():
    import os
    if not os.path.isfile(filteredDatabaseFilename):
        print("Filtering Database")
        with open(filteredDatabaseFilename, "w") as f:
            f.write(convertToCSVString(filterDatabase()))
    if not os.path.isfile(parsedGamesStatesBaseFilename + str(numberOfParseFiles)):
        print("Parsing GameStates")
        parseDatabase()
    if not os.path.isfile(permutedGameStatesBaseFilename + str(numberOfPermuteFiles)):
        print("Permuting GameStates")
        permuteDatabase()
