import random

from Players.Player import Player


class RandomPlayer(Player):
    def getMove(self, board):
        movesAndResultingStates = board.applyMoves(board.generateMoves())
        return random.choice(movesAndResultingStates)[0]

    def won(self):
        pass

    def lost(self):
        pass
