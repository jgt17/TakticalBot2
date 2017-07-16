from collections import deque

from keras.models import load_model


class TakNet:
    def __init__(self, boardSize=5, modelToUse=None, weightsToUse=None):
        self.memory = deque(maxlen=20000000)
        self.gamma = 0.95           # discount rate
        self.epsilon = 1.0          # exploration rate
        self.epsilon_min = 0.01     # min exploration rate
        self.epsilon_decay = 0.995  # exploration rate decay rate
        self.learning_rate = 0.01   # learning rate
        self.batch_size = 10000
        self.batches_per_epoch = 100
        if modelToUse is not None:
            # todo auto-select file from board size (after implement board sizes other than 5)
            self.model = load_model(modelToUse)
        elif weightsToUse is not None:
            self.model = self._buildModel(boardSize, weightsToUse)

    def _buildModel(self, boardSize, weightsToUse=None):
        # create network
        #todo
        raise NotImplementedError

    # add state and target value to training data
    def remember(self, state, stateTargetValue):
        self.memory.append((state, stateTargetValue))

    # add many states and target values to training data
    def rememberAll(self, statesAndTargetValues):
        self.memory += statesAndTargetValues

    def replay(self, batchSize):
        # replay
        # todo
        raise NotImplementedError

    # evaluate the value of game states using the value set of weights
    def evalStateValues(self, states):
        # todo
        return self.model.predict(states)

    # evaluate the value of game states using the self set of weights
    def evalSelfMoves(self, states):
        # todo
        pass

    # evaluate the value of game states using the opponent set of weights
    def evalOpponentMoves(self, states):
        # todo
        pass
