import os.path
import pickle

from Players.AIPlayers.TakNet2.TakNet import TakNet

networkFolder = "NetworkWeights"


def formatNetworkFileName(boardSize, version, attempt=None):
    if attempt is None:
        attemptFolder = ""
        attempt = ""
    else:
        attemptFolder = "/attempt_" + attempt
        attempt = "_attempt_" + attempt
    return networkFolder + "/board_size_" + boardSize + attemptFolder + \
           "/network_board_" + boardSize + attempt + "_epoch_" + version


def formatResultsFileName(boardSize, attempt=None):
    if attempt is None:
        attemptFolder = ""
        attempt = ""
    else:
        attemptFolder = "/attempt_" + attempt
        attempt = "_attempt_" + attempt
    return networkFolder + "/board_size_" + boardSize + attemptFolder + \
           "/board_size_" + boardSize + attempt + "_results"


def formatMemoryFileName(boardSize, attempt=None):
    if attempt is None:
        attemptFolder = ""
        attempt = ""
    else:
        attemptFolder = "/attempt_" + attempt
        attempt = "_attempt_" + attempt
    return networkFolder + "/board_size_" + boardSize + attemptFolder + \
           "/board_size_" + boardSize + attempt + "_memory"


def loadWeights(boardSize=5, version=None, attempt=None):
    if version is None:
        version = "latest"
    try:
        return pickle.load(formatNetworkFileName(boardSize, version, attempt))
    except IOError:
        print("File not found: " + formatNetworkFileName(boardSize, version, attempt))
        exit(1)


def loadNetwork(boardSize=5, version=None, attempt=None):
    if version is None:
        version = "latest"
    return TakNet(boardSize, loadWeights(boardSize, version, attempt))


def saveNetworkWeights(takNet, version, attempt=None):
    saveWeights(takNet.getWeights(), takNet.boardSize, version, attempt)


def saveWeights(weights, boardSize, version, attempt=None):
    try:
        pickle.dump(weights, formatNetworkFileName(boardSize, version, attempt))
    except IOError:
        print("Unable to create file: " + formatNetworkFileName(boardSize, version, attempt))
        exit(2)


def loadResults(boardSize=5, attempt=None):
    try:
        return pickle.load(formatResultsFileName(boardSize, attempt))
    except IOError:
        print("File not found: " + formatResultsFileName(boardSize, attempt))
        exit(1)


def saveResults(results, boardSize=5, attempt=None):
    try:
        pickle.dump(results, formatResultsFileName(boardSize, attempt))
    except IOError:
        print("Unable to create file: " + formatResultsFileName(boardSize, attempt))
        exit(2)
    with open(formatResultsFileName(boardSize, attempt) + "_readable", "w") as f:
        f.write(formatResults(results))


def loadMemory(boardSize=5, attempt=None):
    try:
        return pickle.load(formatMemoryFileName(boardSize, attempt))
    except IOError:
        print("File not found: " + formatMemoryFileName(boardSize, attempt))
        exit(1)


def saveMemory(memory, boardSize=5, attempt=None):
    try:
        pickle.dump(memory, formatResultsFileName(boardSize, attempt))
    except IOError:
        print("Unable to create file: " + formatResultsFileName(boardSize, attempt))
        exit(2)
    with open(formatResultsFileName(boardSize, attempt) + "_readable", "w") as f:
        f.write(formatResults(memory))


def checkIfVersionExists(boardSize, version, attempt=None):
    return os.path.isfile(formatNetworkFileName(boardSize, version, attempt))


# converts results to a nice readable string
def formatResults(results, attempt=None):
    # todo
    raise NotImplementedError


# converts results to a nice readable string, filtered according to the provided parameters
def formatPartialResults(results, version1, attempt=None, version2=None, asWhichPlayer=None, outcomes=None):
    # todo
    # todo add support for opponent version, asWhichPlayer, and results
    raise NotImplementedError

# results structure: version1;version2;(asWhite|asBlack);(won|drawn|lost|unfinished)
