import random

from blist import blist

from DatabaseProcessing import databaseUtil
from Game import TakConstants
from Game.GameManager import GameManager
from Players.AIPlayers.RandomPlayer import RandomPlayer
from Players.AIPlayers.TakNet2 import util
from Players.AIPlayers.TakNet2.TakNet import TakNet
from Players.AIPlayers.TakNet2.TakticalBot import TakticalBot

# include permutations?

gamma = 0.95  # discount rate
epsilon = 1.0  # exploration rate
epsilon_min = 0.01  # min exploration rate
epsilon_decay = 0.995  # exploration rate decay rate
learning_rate = 0.01  # learning rate
minibatch_size = 1000  # number of elements to train on at a time
minibatches_per_batch = 100  # number of minibatches between rotating network weights
batches_per_epoch = 10  # number of batches between saves, checkpoints, etc

memory = blist()
memoryTargetSize = minibatch_size * minibatches_per_batch * batches_per_epoch
examplesPerEpoch = memoryTargetSize
results = dict()
testSize = 500
max_database_epochs = databaseUtil.getNumberOfExamplesInDatabase() // examplesPerEpoch
max_epochs = 1000

boardSize = 5
attempt = None
verbosity = -3


# primary training loop
# verbosity: 0 = no printouts
#            1 = update each epoch
#            2 = update each epoch and batch
#            3 = update each epoch, batch and minibatch
#            if negative, also print results for most recent epoch
def train():
    # load previous epoch or begin from scratch
    currentWeights, currentEpoch, previousResults, previousMemory = loadPreviousOrBeginNew()
    if previousResults is not None:
        global results
        results = previousResults
    if previousMemory is not None:
        global memory
        memory = previousMemory

    # todo add board size recogition to sql filters
    # if beginning from scratch, initialize
    if currentEpoch == -max_database_epochs:
        # save board size and attempt in results
        results["boardSize"] = boardSize
        results["attempt"] = attempt

        saveAndTest(currentWeights, currentEpoch)
        currentEpoch += 1

    # train from database examples
    while currentEpoch < 0:
        currentEpoch += 1
        currentWeights = trainOnDatabase(currentWeights)
        saveAndTest(currentWeights, currentEpoch)
        printEpochUpdate(currentEpoch)

    # train by self-play after training on database
    while currentEpoch <= max_epochs:
        currentEpoch += 1
        currentWeights = trainSelfPlay(currentWeights)
        saveAndTest(currentWeights, currentEpoch)
        printEpochUpdate(currentEpoch)


# train on database examples
def trainOnDatabase(weights):
    return trainForOneEpoch(weights, refillMemoryFromDatabase)


# train via self-play
def trainSelfPlay(weights):
    return trainForOneEpoch(weights, refillMemoryBySelfPlay)


# train for one epoch, using the specified refillFunction to fill the memory with new examples
def trainForOneEpoch(initialWeights, refillFunction):
    staticNetwork = TakNet(boardSize, initialWeights, True)
    dynamicNetwork = TakNet(boardSize, initialWeights, True)
    for batch in range(batches_per_epoch):
        for minibatch in range(minibatches_per_batch):
            refillFunction(staticNetwork, dynamicNetwork)
            replay(dynamicNetwork)
        staticNetwork.setWeights(dynamicNetwork.getWeights())
    return staticNetwork.getWeights()


# generate examples by playing games until memory has at least memoryTargetSize examples in it
def refillMemoryBySelfPlay(staticNetwork, dynamicNetwork):
    # todo
    raise NotImplementedError


def refillMemoryFromDatabase(staticNetwork, dynamicNetwork):
    # todo
    raise NotImplementedError


# load the most recent epoch and results for the specified attempt,
# or initialize if no epochs have been saved in this attempt
def loadPreviousOrBeginNew():
    if util.checkIfVersionExists(boardSize, -max_database_epochs, attempt):
        return loadPrevious()
    else:
        return TakNet(boardSize).getWeights(), -max_database_epochs, None, None


# load the most recent epoch and results for the specified attempt
def loadPrevious():
    epoch = -max_database_epochs
    while util.checkIfVersionExists(boardSize, epoch, attempt):
        epoch += 1
    epoch -= 1
    return util.loadWeights(boardSize, epoch, attempt), \
           epoch, \
           util.loadResults(boardSize, attempt), \
           util.loadMemory(boardSize, attempt)


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
    util.saveMemory(memory, boardSize, attempt)


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
