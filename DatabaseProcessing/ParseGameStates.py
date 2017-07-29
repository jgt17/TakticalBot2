import csv
import pickle

from DatabaseProcessing.databaseUtil import filteredDatabaseFilename, parsedGamesStatesBaseFilename
from DatabaseProcessing.databaseUtil import numberOfParseFiles, gamesPerParseFile
from Game.GameState import GameState
from PlayTakIntegration.NotationConverter import toPTN


# parses csv file of the filtered database (for size=5 and a game that ended in something other than a player resigning)
# to a pickled file which is a list of lists of TrainingGameStates
# the outer list is the games, the inner lists are the results of each successive move of a game


def parseGameStates():
    with open(filteredDatabaseFilename, 'r', newline='') as csvfile:
        parseGamesFromCSV(csvfile)


def parseGamesFromCSV(csvFile):
    csvReader = csv.reader(csvFile, delimiter=';', quotechar='"')
    # necessary to swap out b/c not enough RAM
    r = 0
    for i in range(numberOfParseFiles - 1):
        with open(parsedGamesStatesBaseFilename + str(i), 'wb') as saveLoc:
            pickle.dump([progressUpdate(parseGame(next(csvReader)), row, gamesPerParseFile, r, numberOfParseFiles - 1)
                         for row in range(gamesPerParseFile)], saveLoc)
        r += 1
    with open(parsedGamesStatesBaseFilename + str(numberOfParseFiles - 1), 'wb') as saveLoc:
        pickle.dump(
            [progressUpdate(parseGame(row), i, gamesPerParseFile, numberOfParseFiles - 1, numberOfParseFiles - 1)
             for i, row in enumerate(csvReader)], saveLoc)
    print("Completed parsing all games!")


def progressUpdate(a, i, gamesPerFile, r, numberOfFiles):
    if i % 100 == 0:
        print("Completed parsing game " + str(i) + " of " + str(gamesPerFile) +
              " for file " + r + " of " + numberOfFiles)
    return a


def parseGame(csvRow):
    trainingGameStates = []
    gameState = GameState()
    listOfMoves = csvRow[0].split(',')
    numberOfMoves = len(listOfMoves)
    for i in range(numberOfMoves):
        gameState = gameState.applyMove(toPTN(listOfMoves[i]))
        # print(gameState)
        trainingGameStates.append(gameState)
    return trainingGameStates

if __name__ == "__main__":
    parseGameStates()
