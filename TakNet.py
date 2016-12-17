import TakNet_input

import tensorflow as tf
import os

#the nueral network for TakticalAI
# input format: 5x5x8 (stack x column x row) and 6 (piece counts)
#       convolutions on stacks (conv w/ 1x1x8x20 filter)
#       |         reduction to 5x5 (conv w/ 1x1x20x1 filter)
#       |         |        convolutions on board (conv w/ 3x3x1x20 filter)
#       |         |        |         fully connected layers
#       |         |        |         |     |     |
# 5x5x8 -> 5x5x20 -> 5x5x1 -> 3x3x20 -> 50 -> 25 -> 1
#                                 6 ---^
#                inject piece counts ^

FLAGS = tf.app.flags.FLAGS

# Basic model parameters.
tf.app.flags.DEFINE_integer('batch_size', 128,
                            """Number of games processed in a batch""")
tf.app.flags.DEFINE_string('data_dir', '/NetworkReadyGameStateRepresentations',
                           """Path to the gameState data directory.""")

NUM_EXAMPLES_PER_EPOCH_FOR_TRAIN = TakNet_input.NUM_EXAMPLES_PER_EPOCH_FOR_TRAIN
NUM_EXAMPLES_PER_EPOCH_FOR_EVAL = TakNet_input.NUM_EXAMPLES_PER_EPOCH_FOR_EVAL

MOVING_AVERAGE_DECAY = 0.99999    # The decay to use for the moving average.
NUM_EPOCHS_PER_DECAY = 200.0      # Epochs after which learning rate decays.
LEARNING_RATE_DECAY_FACTOR = 0.1  # Learning rate decay factor.
INITIAL_LEARNING_RATE = 0.1       # Initial learning rate.


# saves activation summaries for later review
def generateActivationSummary(tensor):
    tf.Summary.histogram(tensor.op.name + "/activations", tensor)
    tf.Summary.scalar(tensor.op.name + "sparsity", tf.nn.zero_fraction(tensor))


# helper to create vars with weight decay
# noinspection PyUnusedLocal
def getVarWithWeightDecay(name, shape, stddev=1.0, weightDecayScale=None):
    var = tf.get_variable(name, shape, tf.float32, tf.truncated_normal_initializer(stddev=stddev))
    if weightDecayScale is not None:
        weightDecay = tf.mul(tf.nn.l2_loss(var), weightDecayScale, name="weightLoss")
        tf.add_to_collection("losses", weightDecay)
    return var


# helper to load inputs
# noinspection PyUnusedLocal
def inputs(setNum, evalData):
    dataDir = os.path.join(FLAGS.data_dir, 'gameStates_' + setNum)
    board, pieceCounts, realScore = TakNet_input.inputs(eval_data=evalData,
                                                        data_dir=dataDir,
                                                        batch_size=FLAGS.batch_size)
    return board, pieceCounts, realScore

# create the graph
# using tanh as activation function (gameState can be good for the other player (bad, negative),
#                                                     neutral (0ish), or
#                                                     good (bad for the other player, positive))
def inference(boards, pieceCounts):
    # convolution on stacks
    with tf.variable_scope("stackConv") as scope:
        kernel = getVarWithWeightDecay("weights", [1, 1, 8, 20], 5e-2, 0)
        conv = tf.nn.conv2d(boards, kernel, [1, 1, 1, 1], "VALID")
        biases = tf.get_variable("biases", [20], tf.float32, tf.truncated_normal_initializer())
        stackConv = tf.nn.tanh(tf.nn.bias_add(conv, biases), name=scope.name)
        generateActivationSummary(stackConv)

    # to flat board
    with tf.variable_scope("flattenConv") as scope:
        kernel = getVarWithWeightDecay("weights", [1, 1, 20, 1], 5e-2, 0)
        conv = tf.nn.conv2d(stackConv, kernel, [1, 1, 1, 1], "VALID")
        biases = tf.get_variable("biases", [1], tf.float32, tf.truncated_normal_initializer())
        flattenConv = tf.nn.tanh(tf.nn.bias_add(conv, biases), name=scope.name)
        generateActivationSummary(flattenConv)

    # board convolution
    with tf.variable_scope("boardConv") as scope:
        kernel = getVarWithWeightDecay("weights", [3, 3, 1, 20], 5e-2, 0)
        conv = tf.nn.conv2d(boards, kernel, [1, 1, 1, 1], "VALID")
        biases = tf.get_variable("biases", [1], tf.float32, tf.truncated_normal_initializer())
        boardConv = tf.nn.tanh(tf.nn.bias_add(conv, biases), name=scope.name)
        generateActivationSummary(boardConv)

    # fully connected layers
    with tf.variable_scope("fullyConnected1") as scope:
        # normalize piece counts
        normalizedPieceCounts = tf.div(pieceCounts,
                                       tf.constant([21, 21, 21, 21, 1, 1], tf.float32),
                                       "normalizedPieceCounts")
        # move each example to 1D (-1 -> infer size)
        reshaped = tf.reshape(FLAGS.batchSize, -1)
        injectPieceCounts = tf.concat(1, [reshaped, normalizedPieceCounts], "injectPieceCounts")

        dim = injectPieceCounts.get_shape()[1].value
        weights = getVarWithWeightDecay("weights", [dim, 50], 0.04, 0.01)
        biases = tf.get_variable("biases", [50], tf.float32, tf.truncated_normal_initializer(stddev=0.04))
        fullyConnected1 = tf.tanh(tf.matmul(injectPieceCounts, weights) + biases, name=scope.name)
        generateActivationSummary(fullyConnected1)

    with tf.variable_scope("fullyConnected2") as scope:
        weights = getVarWithWeightDecay("weights", [50, 25], 0.04, 0.01)
        biases = tf.get_variable("biases", [25], tf.float32, tf.truncated_normal_initializer(stddev=0.04))
        fullyConnected2 = tf.tanh(tf.matmul(fullyConnected1, weights) + biases, name=scope.name)
        generateActivationSummary(fullyConnected2)

    with tf.variable_scope("score"):
        weights = getVarWithWeightDecay("weights", [25], 0.04, 0.01)
        bias = tf.get_variable("bias", [1], tf.float32, tf.truncated_normal_initializer(stddev=0.04))
        score = tf.tanh(tf.mul(fullyConnected2, weights) + bias, name=scope.name)
        generateActivationSummary(score)

    return score


# calculates L2 loss on scores and network output
def loss(realScores, networkScores):
    scoresLoss = tf.nn.l2_loss(realScores-networkScores)
    meanScoreLoss = tf.reduce_mean(scoresLoss)
    tf.add_to_collection("losses", meanScoreLoss)

    # total loss includes loss from decaying variables
    return tf.add_n(tf.get_collection("losses"), "Total Loss")


# include summaries of losses in output
def addLossSummaries(totalLoss):
    lossAverages = tf.train.ExponentialMovingAverage(.9, "Avg")
    losses = tf.get_collection("losses")
    lossAveragesOp = lossAverages.apply(losses + [totalLoss])

    for l in losses + [totalLoss]:
        tf.Summary.scalar(l.op.name + "raw", l)
        tf.Summary.scalar(l.op.name, lossAverages.average(l))

    return lossAveragesOp


# training step
def train(totalLoss, globalStep):
    # Variables that affect learning rate.
    numBatchesPerEpoch = NUM_EXAMPLES_PER_EPOCH_FOR_TRAIN / FLAGS.batch_size
    decaySteps = int(numBatchesPerEpoch * NUM_EPOCHS_PER_DECAY)

    # Decay the learning rate exponentially based on the number of steps.
    lr = tf.train.exponential_decay(INITIAL_LEARNING_RATE,
                                    globalStep,
                                    decaySteps,
                                    LEARNING_RATE_DECAY_FACTOR,
                                    staircase=True)
    tf.Summary.scalar('learning_rate', lr)

    # average losses
    lossAveragesOp = addLossSummaries(totalLoss)

    # compute gradients
    with tf.control_dependencies([lossAveragesOp]):
        optimizer = tf.train.GradientDescentOptimizer(lr)
        gradients = optimizer.compute_gradients(totalLoss)

    # apply gradients
    applyGradientOp = optimizer.apply_gradients(gradients, globalStep)

    # add histograms for the weights and biases
    for variable in tf.trainable_variables():
        tf.Summary.histogram(variable.op.name, variable)

    # add histograms for the gradients
    for gradient, variable in gradients:
        if gradient is not None:
            tf.Summary.histogram(variable.op.name + "/gradients", gradient)

    # track moving averages of weights and biases
    variableAverages = tf.train.ExponentialMovingAverage(MOVING_AVERAGE_DECAY, globalStep)
    variableAveragesOp = variableAverages.apply(tf.trainable_variables())

    with tf.control_dependencies([applyGradientOp, variableAveragesOp]):
        trainOp = tf.no_op("Train")

    return trainOp