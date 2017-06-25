import numpy as np

from Players.Player import Player
from Game.GameState import GameState
from Players.AIPlayers.TakNet2.TakNet import TakNet


class TakticalBot(Player):

    # initialize player
    def __init__(self, isWhitePlayer, playerName, boardSize=5, modelToUse=None, weightsToUse=None):
        super().__init__(isWhitePlayer, playerName)
        self.takNet = TakNet(boardSize, modelToUse, weightsToUse)
        raise NotImplementedError

    # choose the best move
    def getMove(self, board: GameState, training=False):
        moves = board.generateMoves()
        # gen opponent moves
        # minimax here
        # if training, compute and remember value of next_state (ie, 4 plies from current state) and new target value
        if self.isWhitePlayer:
            pass  # minimax here instead?
        else:
            pass  # maximin?   # tak is a zero-sum game

    def won(self):
        pass

    def lost(self):
        pass

