import os
import pickle

from DatabaseProcessing.databaseUtil import parsePermuteRatio, gamesPerPermuteFile
from DatabaseProcessing.databaseUtil import parsedGamesStatesBaseFilename, permutedGameStatesBaseFilename


# generates all permuted versions of the parsed games and flattens the list of games


# permute all gameStates
def permuteAll():
    i = 0
    while os.path.isfile(parsedGamesStatesBaseFilename + str(i)):
        with open(parsedGamesStatesBaseFilename + str(i), 'rb') as file:
            generatePermutations(pickle.load(file), i)
        i += 1


# permute all the game states in one parsed game states file
def generatePermutations(games, r):
    for j in range(parsePermuteRatio):
        with open(permutedGameStatesBaseFilename + str(r * parsePermuteRatio + j), 'wb') as saveLoc:
            pickle.dump([permutedGameState
                         for permutations in [progressUpdate(gameState.generatePermutations(), k, l, r, j)
                                              for k, game in
                                              enumerate(games[j * gamesPerPermuteFile:(j + 1) * gamesPerPermuteFile])
                                              for l, gameState in enumerate(game)]
                         for permutedGameState in permutations],
                        saveLoc)


def progressUpdate(a, k, l, r, j):
    if k % 100 == 0 and l == 0:
        print("game " + str(r) + "-" + str(r) + "-" + str(k) + " permuted")
    return a

if __name__ == "__main__":
    permuteAll()
