import copy
import csv
import pickle

from NotationConverter import toPTN

from Game.GameState import GameState
from Players.AIPlayers.TakNet.TrainingGameState import TrainingGameState

# parses csv file of the filtered database (for size=5 and a game that ended in something other than a player resigning)
# to a pickled file which is a list of lists of TrainingGameStates
# the outer list is the games, the inner lists are the results of each successive move of a game
# TrainingGameState has a GameState object and associated score for training the network

filteredDatabaseFilename = "filteredGames"
parsedGamesFilename = "parsedGames"


def parseGamesFromCSV(csvFile):
    csvReader = csv.reader(csvFile, delimiter=';', quotechar='"')
    # fixme
    # assumes between 80,000 and 90,000 ish entries
    # this is terrible practice, but runs orders of magnitude
    # faster than doing it in a way that supports multiple data sets
    # necessary to swap out b/c not enough RAM
    r = 0
    for i in range(8):
        with open("ParsedGameStates/" + parsedGamesFilename + str(i), 'wb') as saveLoc:
            pickle.dump([progressUpdate(parseGame(next(csvReader)), row, r) for row in range(10000)], saveLoc)
        r += 1
    with open("ParsedGameStates/" + parsedGamesFilename + str(8), 'wb') as saveLoc:
        pickle.dump([progressUpdate(parseGame(row), i, 8) for i, row in enumerate(csvReader)], saveLoc)


def progressUpdate(a, i, r):
    if i % 100 == 0:
        print(str(r) + " " + str(i) + " completed")
    return a


def parseGame(csvRow):
    trainingGameStates = []
    gameState = GameState()
    resultIndicator = csvRow[1]
    if resultIndicator == "F-0" or resultIndicator == "R-0":        # win for white
        baseScore = 1
    elif resultIndicator == "0-F" or resultIndicator == "0-R":      # loss for white
        baseScore = -1
    else:                                                           # draw ("1/2-1/2")
        baseScore = 0
    listOfMoves = csvRow[0].split(',')
    numberOfMoves = len(listOfMoves)
    for i in range(numberOfMoves):
        gameState = gameState.applyMove(toPTN(listOfMoves[i]))
        # print(gameState)
        trainingGameStates.append(TrainingGameState(copy.deepcopy(gameState), baseScore/(numberOfMoves-i)))
    return trainingGameStates

if __name__ == "__main__":
    games = []
    with open('RawDatabase/' + filteredDatabaseFilename, 'r', newline='') as csvfile:
        games = parseGamesFromCSV(csvfile)
