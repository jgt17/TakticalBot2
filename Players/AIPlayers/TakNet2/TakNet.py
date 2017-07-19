import pickle

from keras.layers import Input, concatenate
from keras.layers.convolutional import Conv2D, Conv3D
from keras.layers.core import Reshape, Dense
from keras.models import Model
from numpy import unpackbits

from Players.AIPlayers.TakNet2 import util


class TakNet:
    # Basic network structure:
    # Layer 1: Convolutions on individual stacks
    # Layer 2: Convolutions on 3x3 areas
    # Layer 3: Fully connected layer (inject board stats here)
    # Layer 4: Fully connected layer
    # Layer 5: Output Layer

    def __init__(self, boardSize=5, weightsToUse=None):
        self.boardSize = boardSize
        self.layer1NumberOfFilters = (boardSize + 1) * 4
        self.layer2NumberOfFilters = boardSize * 10
        self.layer3Size = boardSize * 20
        self.layer4Size = boardSize * 10
        self.boardMetadataPreprocessingSize = 4
        self.model = self._buildModel(boardSize, weightsToUse)
        if weightsToUse is not None:
            self.setWeights(weightsToUse)

    @staticmethod
    def loadNetwork(boardSize=5, version="latest"):
        try:
            weights = pickle.load(util.networkFolder + "/" + util.formatNetworkFileName(boardSize, version))
            return TakNet(boardSize, weights)
        except IOError:
            print("File not found: " + util.networkFolder + "/" + util.formatNetworkFileName(boardSize, version))
            exit(1)

    def _buildModel(self, boardSize, weightsToUse=None):
        # create network
        # Board Input
        boardIn = Input((boardSize, boardSize, boardSize + 1, 4))
        # Layer 1: Convolution on stacks
        stackConv = Conv3D(self.layer1NumberOfFilters,
                           (1, 1, boardSize + 1),
                           strides=(1, 1, 1),
                           padding='valid',
                           activation='tanh',
                           use_bias=True,
                           kernel_initializer='glorot_uniform',
                           bias_initializer='zeros',
                           kernel_regularizer=None,
                           bias_regularizer=None,
                           activity_regularizer=None,
                           kernel_constraint=None,
                           bias_constraint=None)(boardIn)
        # reshape
        stackConv = (Reshape((boardSize, boardSize, self.layer1NumberOfFilters)))(stackConv)
        # Layer 2: Convolution on 3x3 areas
        boardConv = Conv2D(self.layer2NumberOfFilters,
                           (3, 3),
                           strides=(1, 1),
                           padding='valid',
                           activation='tanh',
                           use_bias=True,
                           kernel_initializer='glorot_uniform',
                           bias_initializer='zeros')(stackConv)
        # Piece Count Inputs
        pieceCounts = Input((6,))
        # Piece Count Preprocessing
        pieceCounts = Dense(self.boardMetadataPreprocessingSize, activation='tanh')(pieceCounts)
        # Merge board and piece counts
        jointInput = concatenate([boardConv, pieceCounts])
        # Layer 3
        layer3 = Dense(self.layer3Size, activation='tanh')(jointInput)
        # Layer 4
        layer4 = Dense(self.layer4Size, activation='tanh')(layer3)
        # Output
        output = Dense(1, activation='tanh')(layer4)

        model = Model(inputs=[boardIn, pieceCounts], outputs=[output])
        return model

    def getWeights(self):
        return self.model.weights

    def setWeights(self, weights):
        self.model.set_weights(weights)

    # evaluate the states according to this networks weights
    def eval(self, states):
        boardStates = list()
        pieceCounts = list()
        for state in states:
            pieceCounts.append(state[1])
            board = state[0]
            if self.boardSize % 2 == 0:
                board.reshape((self.boardSize, self.boardSize, -1))
                board = board[self.boardSize, self.boardSize, :-4]
            board = unpackbits(board)
            board.reshape((self.boardSize, self.boardSize, self.boardSize + 1, 4))
            boardStates.append(board)
        return self.model.predict([boardStates, pieceCounts])
