from GameState import GameState

import tensorflow as tf
import os
import pickle


def _float_feature(value):
    return tf.train.Feature(float_list=tf.train.FloatList(value=[value]))


def _bytes_feature(value):
    return tf.train.Feature(bytes_list=tf.train.BytesList(value=[value]))


# converts the permutedGameStates to suitable tf input
# relevant gamestate is 5x5x6 (board width by board height by carry limit+1) + 6 for stone counts
# converts to 5*5*6+6=156 vector
def convertToTFExamples():
    gameStateReader = GameStateReader()
    outFileCounter = 0
    while not gameStateReader.done:
        filename = os.path.join("NetworkReadyGameStateRepresentations",
                                "gameStates_" + str(outFileCounter) + ".tfrecords")
        # noinspection PyStatementEffect
        open(filename, 'w').close()
        writer = tf.python_io.TFRecordWriter(filename)
        print("Saving to: \"" + filename + "\"")
        for board, score in gameStateReader.readAndConvertGameStates(50000):
            example = tf.train.Example(features=tf.train.Features(feature={
                "score:": _float_feature(score),
                'boardData': _bytes_feature(board)}))
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

if __name__ == "__main__":
    convertToTFExamples()
