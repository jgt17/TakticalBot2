from keras.models import load_model

from collections import deque


class TakNet:
    def __init__(self, boardSize=5, modelToUse=None, weightsToUse=None):
        self.memory = deque(maxlen=2000000)
        self.gamma = 0.95           # discount rate
        self.epsilon = 1.0          # exploration rate
        self.epsilon_min = 0.01     # min exploration rate
        self.epsilon_decay = 0.995  # exploration rate decay rate
        self.learning_rate = 0.01   # learning rate
        if modelToUse is not None:
            # todo auto-select file from board size (after implement board sizes other than 5)
            self.model = load_model(modelToUse)
        elif weightsToUse is not None:
            self.model = self._buildModel(boardSize, weightsToUse)

    def _buildModel(self, boardSize, weightsToUse=None):
        # create network
        raise NotImplementedError

    # add state and target value to training data
    def remember(self, state, nextStateTargetValue):
        self.memory.append((state, nextStateTargetValue))

    def replay(self, batchSize):
        # replay
        raise NotImplementedError

    # evaluate the value of game states
    def eval(self, states):
        return self.model.predict(states)