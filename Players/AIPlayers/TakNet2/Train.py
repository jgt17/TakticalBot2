import random

from blist import blist

from Game import TakConstants
from Game.GameManager import GameManager
from Players.AIPlayers.RandomPlayer import RandomPlayer
from Players.AIPlayers.TakNet2.TakticalBot import TakticalBot, util, TakNet

# include permutations?

gamma = 0.95  # discount rate
epsilon = 1.0  # exploration rate
epsilon_min = 0.01  # min exploration rate
epsilon_decay = 0.995  # exploration rate decay rate
learning_rate = 0.01  # learning rate
minibatch_size = 1000  # number of elements to train on at a time
minibatches_per_batch = 100  # number of minibatches between rotating network weights
batches_per_epoch = 10  # number of batches between saves, checkpoints, etc
max_epochs = 1000

memory = blist()
results = dict()
testSize = 500

boardSize = 5
attempt = None
verbosity = -3

databaseFileLocation = "RawDatabase"


# primary training loop
# verbosity: 0 = no printouts
#            1 = update each epoch
#            2 = update each epoch and batch
#            3 = update each epoch, batch and minibatch
#            if negative, also print results for most recent epoch
def train():
    # load previous epoch or begin from scratch
    initialWeights, currentEpoch, previousResults = loadPreviousOrBeginNew()
    if previousResults is not None:
        global results
        results = previousResults

    # if beginning from scratch, train on database
    if currentEpoch < 0:
        # save board size in results
        results["boardSize"] = boardSize

        saveAndTest(initialWeights, currentEpoch)
        newWeights = trainOnDatabase(databaseFileLocation, initialWeights)
        currentEpoch += 1
        saveAndTest(newWeights, currentEpoch)
        printEpochUpdate(currentEpoch)
    else:
        newWeights = initialWeights

    # train by self-play after training on database
    while currentEpoch <= max_epochs:
        currentEpoch += 1
        newWeights = trainSelfPlay(newWeights)
        saveAndTest(newWeights, currentEpoch)
    printEpochUpdate(currentEpoch)


# train on database examples
def trainOnDatabase(filepath, weights):
    # todo
    raise NotImplementedError


# train via self-play
def trainSelfPlay(weights):
    # todo
    raise NotImplementedError


# load the most recent epoch and results for the specified attempt,
# or initialize if no epochs have been saved in this attempt
def loadPreviousOrBeginNew():
    if util.checkIfVersionExists(boardSize, -1, attempt):
        return loadPrevious()
    else:
        return TakNet(boardSize).getWeights(), -1, None


# load the most recent epoch and results for the specified attempt
def loadPrevious():
    epoch = -1
    while util.checkIfVersionExists(boardSize, epoch, attempt):
        epoch += 1
    epoch -= 1
    return util.loadWeights(boardSize, epoch, attempt), epoch, util.loadResults(boardSize, attempt)


# format and print the update between epochs
def printEpochUpdate(epoch):
    if verbosity == 0:
        return

    print("Completed epoch " + str(epoch) + " of attempt " + str(attempt) + " for board size " + str(boardSize))

    if verbosity < 0:
        print(util.formatPartialResults(results, attempt, epoch))


# add state and target value to training data
def remember(state, stateTargetValue):
    memory.append((state, stateTargetValue))


# add many states and target values to training data
def rememberAll(statesAndTargetValues):
    memory.extend(statesAndTargetValues)


# randomly select examples from the buffer to train on
def replay(network):
    sample = random.sample(range(len(memory)), minibatch_size)
    minibatch = [memory[s] for s in sample]
    for example in minibatch:
        memory.remove(example)
    network.train(minibatch)


# save and test a new set of weights
def saveAndTest(weights, version):
    util.saveWeights(weights, version, attempt)
    test(version)
    util.saveResults(results, boardSize, attempt)


# test a version against a random player and each version of the network, including itself
def test(version):
    currentResults = dict()
    currentResults["random"] = _primaryTestHelper(version, "random")
    otherVersion = -1
    while util.checkIfVersionExists(boardSize, otherVersion, attempt):
        currentResults[otherVersion] = _primaryTestHelper(version, otherVersion)
        otherVersion += 1
    results[version] = currentResults


def _primaryTestHelper(versionToBeTested, otherVersion):
    return {"as_white": _secondaryTestHelper(versionToBeTested, otherVersion, True, attempt),
            "as_black": _secondaryTestHelper(versionToBeTested, otherVersion, False, attempt)}


def _secondaryTestHelper(versionToBeTested, otherVersion, versionTestedIsWhite, attemptToUse=None):
    gamesWon = 0
    gamesDrawn = 0
    gamesLost = 0
    gamesOvertime = 0
    playerToBeTested = TakticalBot(versionTestedIsWhite,
                                   boardSize=boardSize,
                                   version=versionToBeTested,
                                   attempt=attemptToUse)
    if otherVersion is "random":
        otherPlayer = RandomPlayer(False)
    else:
        otherPlayer = TakticalBot(not versionTestedIsWhite,
                                  boardSize=boardSize,
                                  version=otherVersion,
                                  attempt=attemptToUse)
    if versionTestedIsWhite:
        gameManager = GameManager(playerToBeTested, otherPlayer, boardSize)
    else:
        gameManager = GameManager(otherPlayer, playerToBeTested, boardSize)
    for i in range(testSize):
        gameResult = gameManager.playGame()[2]  # only care about the final status if the game
        if gameResult == TakConstants.whiteWon:
            if versionTestedIsWhite:
                gamesWon += 1
            else:
                gamesLost += 1
        elif gameResult == TakConstants.draw:
            gamesDrawn += 1
        elif gameResult == TakConstants.blackWon:
            if versionTestedIsWhite:
                gamesLost += 1
            else:
                gamesWon += 1
        else:
            gamesOvertime += 1
    return {"won": gamesWon / testSize, "drawn": gamesDrawn / testSize,
            "lost": gamesLost / testSize, "unfinished": gamesOvertime / testSize}


if __name__ == "__main__":
    train()
