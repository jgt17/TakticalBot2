# from GameState import GameState
# from TrainingGameState import TrainingGameState

import pickle

# generates all permuted versions of the parsed games and flattens the list of games

parsedGamesFilename = "parsedGames"
permutedGamesStatesFilename = "permutedGameStates"

# again, some bad practice here, but I only need to work with the one data set, and it it much faster


def generatePermutations(games, r):
    blockSize = 1000
    for j in range(10):
        with open("PermutedGameStates/" + permutedGamesStatesFilename + "_" + str(r) + "_" + str(j), 'wb') as saveLoc:
            pickle.dump([permutedGameState
                         for permutations in [progressUpdate(gameState.generatePermutations(), k, l, r, j)
                                              for k, game in enumerate(games[j*blockSize:(j+1)*blockSize])
                                              for l, gameState in enumerate(game)]
                         for permutedGameState in permutations],
                        saveLoc)


def progressUpdate(a, k, l, r, j):
    if k % 100 == 0 and l == 0:
        print("game " + str(r) + "-" + str(r) + "-" + str(k) + " permuted")
    return a

if __name__ == "__main__":
    permutedGames = []
    for i in range(9):
        with open("ParsedGameStates/" + parsedGamesFilename + str(i), 'rb') as file:
            generatePermutations(pickle.load(file), i)
