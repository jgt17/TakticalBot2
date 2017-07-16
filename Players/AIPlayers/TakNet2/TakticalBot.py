from random import random, choice

from Players.Player import Player
from Game.GameState import GameState
from Players.AIPlayers.TakNet2.TakNet import TakNet

from Players.AIPlayers.TakNet2.Train import gamma, epsilon
# todo decide where to store training variables


class TakticalBot(Player):

    # initialize player
    def __init__(self, isWhitePlayer, playerName, boardSize=5, modelToUse=None, weightsToUse=None):
        super().__init__(isWhitePlayer, playerName)
        self.takNet = TakNet(boardSize, modelToUse, weightsToUse)
        raise NotImplementedError

    # choose a move
    def getMove(self, board: GameState, training=False):
        if training and random() < epsilon:
            # do random move for exploration
            move, oppState = choice(board.applyMoves(board.generateMoves()))
            nextState = self.__worstOppMove(oppState)
        else:
            _, move, nextState = self.evalMoves(board)

        if training:
            # which of these to use? both? todo
            # remember what really happened
            self.remember(board, gamma * self.takNet.evalStateValues([nextState])[0])
            # remember minimax prediction
            self.remember(nextState, self.targetValue(nextState))

        return move

    # calculate value of moves
    def evalMoves(self, board):
        if self.isWhitePlayer:      # tak is zero-sum
            minStep = min
            maxStep = max
        else:
            minStep = max
            maxStep = min
        selfMoves = board.generateMoves()
        selfMovesAndNewStates = board.applyMoves(selfMoves)
        moves = list()
        worstNextStates = list()
        for move, newState in selfMovesAndNewStates:
            moves.append(move)
            finalStates = list()
            for _, finalState in newState.applyMoves(newState.generateMoves()):
                finalStates.append(finalState)
            moveValue, worstNextState = minStep(
                zip(self.takNet.evalOpponentMoves(self.asExamples(finalStates)), finalStates))
            worstNextStates.append(worstNextState)
        valueMoveAndState = maxStep(
            zip(self.takNet.evalSelfMoves(self.asExamples(worstNextStates)), moves, worstNextStates))
        return valueMoveAndState

    # get worst case opponent move, for eval use in exploration cases
    def __worstOppMove(self, oppState):
        if self.isWhitePlayer:  # tak is zero-sum
            minStep = min
        else:
            minStep = max
        finalStates = list()
        for _, finalState in oppState.applyMoves(oppState.generateMoves()):
            finalStates.append(finalState)
        _, worstNextState = minStep(
            zip(self.takNet.evalOpponentMoves(self.asExamples(finalStates)), finalStates))
        return worstNextState

    # convert a list of GameStates into a list of TakNet-ready examples
    def asExamples(self, states):
        # todo
        pass

    # calculate the new target value of a state
    # here rather than in Train.py or TakNet.py to avoid needing to re-instantiate the GameStates
    def targetValue(self, state):
        result = state.checkVictory()
        if result != 2:     # if game ended
            return result   # -1 if white lost, 0 if draw, 1 if white won
        else:
            _, _, nextState = self.evalMoves(state)
            return gamma * self.takNet.evalStateValues(self.asExamples([nextState]))[0]

    # add a gameState and it's permutations, with target values, to takNet's training buffer
    def remember(self, gameState, targetValue):
        normalPermutations = gameState.generateNormalPermutations()
        invertedPermutations = gameState.generateInvertedPermutations()
        permutations = list()
        for permutation in normalPermutations:
            permutations.append((permutation, targetValue))
        for permutation in invertedPermutations:
            permutations.append((permutation, -targetValue))
        self.takNet.rememberAll(permutations)

    def won(self):
        pass

    def lost(self):
        pass
