# for determining end-of-game, only the top stones on each stack matter
# this is a flattened version of the board containing only those pieces
# making it easier to find win conditions
from Stack import Stack

class FlatBoard:

    def __init__(self, gameState):
        self.flatBoard = [[0 for _ in range(gameState.boardSize)] for _ in range(gameState.boardSize)]
        self.whitePiecesLeft = gameState.__whitePiecesRemaining
        self.blackPiecesLeft = gameState.__blackPiecesRemaining
        self.turnIndicator = gameState.__turnIndicator
        for i in range(gameState.boardSize):
            for j in range(gameState.boardSize):
                piece = gameState.__board[i][j].top()
                if piece != 2 and piece != -2:
                    self.flatBoard[i][j] = piece

    def checkVictory(self):
        r = self.checkRoadVictory()
        if r != 0:
            return r
        elif self.blackPiecesLeft == 0 or self.whitePiecesLeft == 0 or self.boardIsCovered():
            return self.checkFlatVictory()
        else:
            return 2

    def __checkRoadVictory(self):
        connectedComponents = self.__getConnectedComponents()
        for cc in connectedComponents:
            if
        # todo
        return 2

    def __checkFlatVictory(self):
        # todo
        return 0

    def __boardIsCovered(self):
        # todo
        return 2

    def __getConnectedComponents(self):
        # todo
        return