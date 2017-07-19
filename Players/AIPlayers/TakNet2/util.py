import os.path
import pickle

from Players.AIPlayers.TakNet2.TakNet import TakNet

networkFolder = "NetworkWeights"


def formatNetworkFileName(boardSize, version):
    return networkFolder + "/network_board_" + boardSize + "_epoch_" + version


def loadWeights(boardSize=5, version=None):
    if version is None:
        version = "latest"
    try:
        return pickle.load(formatNetworkFileName(boardSize, version))
    except IOError:
        print("File not found: " + formatNetworkFileName(boardSize, version))
        exit(1)


def loadNetwork(boardSize=5, version=None):
    if version is None:
        version = "latest"
    return TakNet(boardSize, loadWeights(boardSize, version))


def saveWeights(takNet, version):
    try:
        weights = takNet.getWeights()
        pickle.dump(weights, formatNetworkFileName(takNet.boardSize, version))
    except IOError:
        print("Unable to create file: " + formatNetworkFileName(takNet.boardSize, version))
        exit(2)


def checkIfVersionExists(boardSize, version):
    return os.path.isfile(formatNetworkFileName(boardSize, version))
