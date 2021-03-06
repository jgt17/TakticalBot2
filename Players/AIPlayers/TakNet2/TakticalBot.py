from random import random, choice

from Game.GameState import GameState
from Players.AIPlayers.TakNet2 import Train, util
from Players.AIPlayers.TakNet2.TakNet import TakNet
from Players.Player import Player


class TakticalBot(Player):

    # initialize player
    def __init__(self, isWhitePlayer, playerName=None, boardSize=5, version=None, attempt=None,
                 evaluationWeights=None, selectionWeights=None, training=False,
                 evaluationNetwork=None, selectionNetwork=None):
        super().__init__(isWhitePlayer, playerName)
        if version is not None:
            weights = util.loadWeights(boardSize, version, attempt)
            self.evaluationTakNet = TakNet(boardSize, weights)
            self.selectionTakNet = TakNet(boardSize, weights)
        else:
            if evaluationNetwork is None:
                self.evaluationTakNet = TakNet(boardSize, evaluationWeights)  # target network
            else:
                self.evaluationTakNet = evaluationNetwork
            if selectionNetwork is None:
                self.selectionTakNet = TakNet(boardSize, selectionWeights)  # "live" network
            else:
                self.selectionTakNet = selectionNetwork
        self.training = training
        raise NotImplementedError

    # choose a move
    def getMove(self, board: GameState, training=None):
        if training is None:
            training = self.training
        if training and random() < Train.epsilon:
            # do random move for exploration
            move, oppState = choice(board.applyMoves(board.generateMoves()))
            nextState = self.__worstOppMove(oppState)
        else:
            _, move, nextState = self.evalMoves(board)

        if training:
            # remember what really happened
            self.remember(board, Train.gamma * self.evaluationTakNet.eval([nextState])[0])
            # (don't) remember minimax prediction
            # self.remember(nextState, self.targetValue(nextState))

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
                zip(self.selectionTakNet.eval(self.asExamples(finalStates)), finalStates))
            worstNextStates.append(worstNextState)
        valueMoveAndState = maxStep(
            zip(self.selectionTakNet.eval(self.asExamples(worstNextStates)), moves, worstNextStates))
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
            zip(self.selectionTakNet.eval(self.asExamples(finalStates)), finalStates))
        return worstNextState

    # convert a list of GameStates into a list of TakNet-ready examples
    def asExamples(self, states):
        return [state.toNetworkInputs() for state in states]

    # calculate the new target value of a state
    # here rather than in Train.py or TakNet.py to avoid needing to re-instantiate the GameStates
    def targetValue(self, state):
        result = state.checkVictory()
        if result != 2:     # if game ended
            return result   # -1 if white lost, 0 if draw, 1 if white won
        else:
            _, _, nextState = self.evalMoves(state)
            return Train.gamma * self.evaluationTakNet.eval(self.asExamples([nextState]))[0]

    # add a gameState and it's permutations, with target values, to takNet's training buffer
    def remember(self, gameState, targetValue):
        normalPermutations = gameState.generateNormalPermutations()
        invertedPermutations = gameState.generateInvertedPermutations()
        permutations = list()
        for permutation in normalPermutations:
            permutations.append((permutation, targetValue))
        for permutation in invertedPermutations:
            permutations.append((permutation, -targetValue))
        Train.rememberAll(permutations)

    def won(self):
        pass

    def lost(self):
        pass
