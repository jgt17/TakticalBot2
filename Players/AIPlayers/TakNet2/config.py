gamma = 0.95  # discount rate
epsilon = 1.0  # exploration rate
epsilon_min = 0.01  # min exploration rate
epsilon_decay = 0.995  # exploration rate decay rate
learning_rate = 0.01  # learning rate
minibatch_size = 1000  # number of elements to train on at a time
minibatches_per_batch = 100  # number of minibatches between rotating network weights
batches_per_epoch = 10  # number of batches between saves, checkpoints, etc

memoryTargetSize = minibatch_size * minibatches_per_batch * batches_per_epoch
examplesPerEpoch = memoryTargetSize
testSize = 500
max_epochs = 1000

boardSize = 5
attempt = None
verbosity = -3
