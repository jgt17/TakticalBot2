from collections import deque

# todo training loop
# todo save, load training state
# todo log training, results
# include permutations?

memory = deque(maxlen=20000000)
gamma = 0.95  # discount rate
epsilon = 1.0  # exploration rate
epsilon_min = 0.01  # min exploration rate
epsilon_decay = 0.995  # exploration rate decay rate
learning_rate = 0.01  # learning rate
minibatch_size = 10000  # number of elements to train on at a time
minibatches_per_batch = 100  # number of minibatches between rotating network weights
batches_per_epoch = 20  # number of batches between saves, checkpoints, etc


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
