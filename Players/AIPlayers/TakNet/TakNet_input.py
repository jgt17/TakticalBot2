import os
import pickle

import tensorflow as tf


def _float_feature(value):
    return tf.train.Feature(float_list=tf.train.FloatList(value=[value]))


def _bytes_feature(value):
    return tf.train.Feature(bytes_list=tf.train.BytesList(value=[value]))

inputsDirName = "NetworkReadyGameStateRepresentations"
NUM_EXAMPLES_PER_EPOCH_FOR_TRAIN = 50000
NUM_EXAMPLES_PER_EPOCH_FOR_EVAL = 10000


# converts the permutedGameStates to suitable tf input
# relevant gameState is 5x5x6 (board width by board height by carry limit+1) + 6 for stone counts
# converts to 5*5*6+6=156 vector
def convertToTFExamples():
    gameStateReader = GameStateReader()
    outFileCounter = 0
    while not gameStateReader.done:
        filename = os.path.join(inputsDirName,
                                "gameStates_" + str(outFileCounter) + ".tfrecords")
        # noinspection PyStatementEffect
        open(filename, 'w').close()
        writer = tf.python_io.TFRecordWriter(filename)
        print("Saving to: \"" + filename + "\"")
        for board, pieceCounts, score in gameStateReader.readAndConvertGameStates(50000):
            example = tf.train.Example(features=tf.train.Features(feature={
                "score:": _float_feature(score),
                "pieceCounts": _bytes_feature(pieceCounts),
                "boardData": _bytes_feature(board)}))
            writer.write(example.SerializeToString())
        writer.close()
        outFileCounter += 1


# helper class for reading in states from across files
class GameStateReader:
    def __init__(self, directory="PermutedGameStates", baseFileName="permutedGameStates"):
        self.i = 0
        self.j = 0
        self.done = False
        self.directory = directory
        self.baseFileName = baseFileName
        self.currentIndex = 0
        self.currentGameStates = None

    # reads numberOfStates states and returns a list of them
    def readGameStates(self, numberOfStates):
        if self.currentGameStates is None:
            try:
                with open(os.path.join(self.directory,
                                       self.baseFileName + "_" + str(self.i) + "_" + str(self.j)),
                          'rb') as file:
                    print("Reading from: \"" + file.name + "\" at index: " + str(self.currentIndex))
                    self.currentGameStates = pickle.load(file)
                    print("There are " + str(len(self.currentGameStates)) + " gameStates in this file.")
            except FileNotFoundError:
                # all files processed
                if self.j == 0:
                    self.done = True
                    return []
                else:
                    self.i += 1
                    self.j = 0
                    self.currentIndex = 0
                    return self.readGameStates(numberOfStates)
        else:
            print("    Continuing to read the same file from index " + str(self.currentIndex))
        states = self.currentGameStates[self.currentIndex:self.currentIndex + numberOfStates]
        self.currentIndex += len(states)
        if len(states) < numberOfStates:
            self.j += 1
            self.currentIndex = 0
            self.currentGameStates = None
            return states + self.readGameStates(numberOfStates-len(states))
        else:
            return states

    # reads numberOfStates, converts them to tf format, and returns a list of them
    def readAndConvertGameStates(self, numberOfStates):
        return [state.toNetworkInputs() for state in self.readGameStates(numberOfStates)]


# generates a batch of examples
def generateBatch(board, pieceCounts, realScore, minQueueExamples, batchSize, shuffle=True):
    # Create a queue that shuffles the examples, and then
    # read 'batch_size' images + labels from the example queue.
    numPreprocessThreads = 16
    if shuffle:
        boardBatch, pieceCountBatch, realScoreBatch = tf.train.shuffle_batch(
                                                        [board, pieceCounts, realScore],
                                                        batch_size=batchSize,
                                                        num_threads=numPreprocessThreads,
                                                        capacity=minQueueExamples + 3 * batchSize,
                                                        min_after_dequeue=minQueueExamples)
    else:
        boardBatch, pieceCountBatch, realScoreBatch = tf.train.batch(
                                                        [board, pieceCounts, realScore],
                                                        batch_size=batchSize,
                                                        num_threads=numPreprocessThreads,
                                                        capacity=minQueueExamples + 3 * batchSize,
                                                        min_after_dequeue=minQueueExamples)

    return boardBatch, pieceCountBatch, tf.reshape(realScoreBatch, [batchSize])


# read in gameStates from the file queue
def readGameStates(fileNameQueue):
    reader = tf.TFRecordReader("ExampleReader")
    key, value = reader.read(fileNameQueue)
    #val = tf.Print(value, [value])
    example = tf.parse_single_example(value, features={"score:": tf.FixedLenFeature([], tf.float32),
                                                       "pieceCounts": tf.FixedLenFeature([], tf.string),
                                                       "boardData": tf.FixedLenFeature([], tf.string)})
    #printExample = tf.Print(example, [example])
    score = tf.reshape(example["score:"], [1])
    pieceCounts = tf.reshape(tf.cast(tf.decode_raw(example["pieceCounts"], tf.uint8), tf.float32), [6])
    board = tf.reshape(tf.cast(tf.decode_raw(example["boardData"], tf.int8), tf.float32), [5, 5, 8])

    # def correct(x):
    #   tf.cond(tf.equal(x, tf.constant(255, tf.float32)), lambda: tf.constant(-1, tf.float32), lambda: x)

    # correctedBoard = tf.reshape(tf.map_fn(correct, board), [5, 5, 8])

    return board, pieceCounts, score


# load inputs
def inputs(evalData, dataDir, batchSize):
    # get different data for evaluation and training (every 10th example file is set aside for evaluations)
    if evalData:
        fileNames = [dataDir + "/gameStates_%i.tfrecords" % i for i in range(894) if i % 10 == 0]
        numExamplesPerEpoch = NUM_EXAMPLES_PER_EPOCH_FOR_EVAL
    else:
        fileNames = [dataDir + "/gameStates_%i.tfrecords" % i for i in range(894) if i % 10 != 0]
        numExamplesPerEpoch = NUM_EXAMPLES_PER_EPOCH_FOR_TRAIN

    # ensure each file exists
    for f in fileNames:
        if not tf.gfile.Exists(f):
            string = "Could not find \"" + f + "\""
            raise ValueError(string)

    fileNameQueue = tf.train.string_input_producer(fileNames)
    board, pieceCounts, realScore = readGameStates(fileNameQueue)

    # ensure that the random shuffling has good mixing properties.
    minFractionOfExamplesInQueue = 0.4
    minQueueExamples = int(numExamplesPerEpoch * minFractionOfExamplesInQueue)

    # generate a batch of examples
    return generateBatch(board, pieceCounts, realScore, minQueueExamples, batchSize, shuffle=True)


if __name__ == "__main__":
    if os.path.isfile(os.path.join(inputsDirName, "gameStates_0.tfrecords")):
        print("It appears that the inputs have already been processed.\n"
              "Please Delete the contents of /" + inputsDirName + " to continue.")
    else:
        convertToTFExamples()
