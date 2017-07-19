from collections import deque

from Game import TakConstants
from Game.GameManager import GameManager
from Players.AIPlayers.RandomPlayer import RandomPlayer
from Players.AIPlayers.TakNet2.TakticalBot import TakticalBot, util

# todo training loop
# todo save, load training state
# todo log training, results
# include permutations?

memory = deque(maxlen=1000000)
gamma = 0.95  # discount rate
epsilon = 1.0  # exploration rate
epsilon_min = 0.01  # min exploration rate
epsilon_decay = 0.995  # exploration rate decay rate
learning_rate = 0.01  # learning rate
minibatch_size = 10000  # number of elements to train on at a time
minibatches_per_batch = 100  # number of minibatches between rotating network weights
batches_per_epoch = 20  # number of batches between saves, checkpoints, etc

results = dict()
testSize = 500

boardSize = 5


# add state and target value to training data
def remember(state, stateTargetValue):
    memory.append((state, stateTargetValue))


# add many states and target values to training data
def rememberAll(statesAndTargetValues):
    memory.extend(statesAndTargetValues)


def replay(self, batchSize):
    # replay
    # todo
    raise NotImplementedError


def test(version):
    currentResults = dict()
    currentResults["random"] = _primaryTestHelper(version, "random")
    otherVersion = -1
    while util.checkIfVersionExists(boardSize, otherVersion):
        currentResults[otherVersion] = _primaryTestHelper(version, otherVersion)
        otherVersion += 1
    results[version] = currentResults


def _primaryTestHelper(versionToBeTested, otherVersion):
    return {"as_white": _secondaryTestHelper(versionToBeTested, otherVersion, True),
            "as_black": _secondaryTestHelper(versionToBeTested, otherVersion, False)}


def _secondaryTestHelper(versionToBeTested, otherVersion, versionTestedIsWhite):
    gamesWon = 0
    gamesDrawn = 0
    gamesLost = 0
    gamesOvertime = 0
    playerToBeTested = TakticalBot(versionTestedIsWhite, boardSize=boardSize, version=versionToBeTested)
    if otherVersion is "random":
        otherPlayer = RandomPlayer(False)
    else:
        otherPlayer = TakticalBot(versionTestedIsWhite, boardSize=boardSize, version=otherVersion)
    gameManager = GameManager(playerToBeTested, otherPlayer, boardSize)
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


# converts results to a nice readable string
def formatResults():
    # todo
    pass
