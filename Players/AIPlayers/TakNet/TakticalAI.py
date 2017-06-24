import time

from Players.AIPlayers import TakNet
import tensorflow as tf
from Game.GameState import GameState

from Game.TakException import TakException
from Players.AIPlayers.TakNet.MiniMax import miniMax

NETWORK_TO_USE = ""


def playTak():
    currentGameState = GameState()
    print(currentGameState)

    with tf.Graph().as_default():
        # make graph to apply the network
        # boards = tf.placeholder(tf.float32)
        # pieceCounts = tf.placeholder(tf.float32)
        # inferenceOp = TakNet.inference(boards, pieceCounts)

        # mimic training graph structure to load variables
        globalStep = tf.contrib.framework.get_or_create_global_step()
        # get data
        boards, pieceCounts, realScores = TakNet.inputs(False)
        # instantiate prediction graph
        scores = TakNet.inference(boards, pieceCounts)
        # calculate loss
        totalLoss, meanLoss = TakNet.loss(realScores, scores)
        # train for one batch and update parameters
        # noinspection PyUnusedLocal
        trainOp = TakNet.train(totalLoss, meanLoss, globalStep)

        with tf.Session() as session:
            # restore weights from model in Network folder
            tf.train.Saver().restore(session, tf.train.latest_checkpoint("Network"))

            tf.get_variable_scope().reuse_variables()
            boards2 = tf.placeholder(tf.float32)
            pieceCounts2 = tf.placeholder(tf.float32)
            inferenceOp = TakNet.inference(boards2, pieceCounts2)

            while True:
                try:
                    if currentGameState.turnIndicator == 1:
                        startTime = time.time()
                        move = miniMax(currentGameState, session, inferenceOp, boards2, pieceCounts2)
                        endTime = time.time()
                        print("TakticalBot: "+move)
                        print("Time: " + str(endTime-startTime))
                    else:
                        move = input("Player:      ")
                        if move == "quit":
                            break
                    currentGameState = currentGameState.applyMove(move)
                    print(currentGameState)
                    winner = currentGameState.checkVictory()
                    if winner != 2:
                        if winner == 1:
                            print("TakticalBot Won!")
                        elif winner == -1:
                            print("You Won!")
                        else:
                            print("It was a draw")
                        break
                except TakException as exception:
                    print(exception)
                    continue

if __name__ == "__main__":
    playTak()
