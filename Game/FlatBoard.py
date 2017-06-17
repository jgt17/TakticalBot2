# for determining end-of-game, only the top stones on each stack matter
# this is a flattened version of the board containing only those pieces
# making it easier to find win conditions

from Game.GameState import GameState

class FlatBoard:

    def __init__(self, gameState):
        self.flatBoard = [[0 for _ in range(gameState.boardSize)] for _ in range(gameState.boardSize)]
        self.whitePiecesLeft = gameState.whitePiecesRemaining
        self.blackPiecesLeft = gameState.blackPiecesRemaining
        self.turnIndicator = gameState.turnIndicator
        self.boardSize = gameState.boardSize
        for i in range(gameState.boardSize):
            for j in range(gameState.boardSize):
                self.flatBoard[i][j] = gameState.board[i][j].top()
        self.winner = self.checkVictory()

    def checkVictory(self):
        r = self.__checkRoadVictory()
        if not (r == GameState.ongoing or r == GameState.draw):      # road victory takes priority over flats victory
            return r
        elif self.blackPiecesLeft == 0 or self.whitePiecesLeft == 0 or self.__boardIsCovered():
            return self.__checkFlatVictory()
        else:
            return GameState.ongoing

    def __checkRoadVictory(self):
        boardSize = len(self.flatBoard)
        leftEdge = set()
        bottomEdge = set()
        for i in range(boardSize):
            leftEdge.add((-1, i))
            bottomEdge.add((i, -1))
        if self.__roadExists(leftEdge, boardSize, "horizontal", 1)\
                or self.__roadExists(bottomEdge, boardSize, "vertical", 1):
            return GameState.whiteWon
        elif self.__roadExists(leftEdge, boardSize, "horizontal", -1)\
                or self.__roadExists(bottomEdge, boardSize, "vertical", -1):
            return GameState.blackWon
        else:
            return GameState.ongoing

    def __checkFlatVictory(self):
        whiteCount, blackCount, _, _, _, _ = self.getPieceCounts()

        if whiteCount > blackCount:
            return GameState.whiteWon
        elif blackCount > whiteCount:
            return GameState.blackWon
        else:
            return GameState.draw

    def getPieceCounts(self):
        whiteCount = 0
        blackCount = 0
        whiteStandingCount = 0
        blackStandingCount = 0
        whiteCapstoneCount = 0
        blackCapstoneCount = 0

        for file in self.flatBoard:
            for piece in file:
                if piece == 1:
                    whiteCount += 1
                elif piece == -1:
                    blackCount += 1
                elif piece == 2:
                    whiteStandingCount += 1
                elif piece == -2:
                    blackStandingCount += 1
                elif piece == 3:
                    whiteCapstoneCount += 1
                elif piece == -3:
                    blackCapstoneCount += 1

        return whiteCount, blackCount, whiteStandingCount, blackStandingCount, whiteCapstoneCount, blackCapstoneCount

    def __boardIsCovered(self):
        for file in self.flatBoard:
            for piece in file:
                if piece == 0:
                    return False
        return True

    # fixme
    def __roadExists(self, openSet, size, direction, player):
        closedSet = set()
        openSet = openSet.copy()
        while openSet:
            curr = openSet.pop()
            if (direction == "horizontal" and curr[0] == size - 1) or (direction == "vertical" and curr[1] == size - 1):
                return True
            closedSet.add(curr)
            adj = self.__getAdj(curr)
            for neighbor in adj:
                piece = self.flatBoard[neighbor[0]][neighbor[1]]
                if neighbor not in openSet and neighbor not in closedSet and piece * player > 0 and piece % 2 != 0:
                    openSet.add(neighbor)

    def __getAdj(self, loc):
        i = loc[0]
        j = loc[1]
        adj = set()
        if self.__inBounds(i - 1, j):
            adj.add((i - 1, j))
        if self.__inBounds(i + 1, j):
            adj.add((i + 1, j))
        if self.__inBounds(i, j - 1):
            adj.add((i, j - 1))
        if self.__inBounds(i, j + 1):
            adj.add((i, j + 1))
        return adj

    def __inBounds(self, file, rank):
        return 0 <= file < self.boardSize and 0 <= rank < self.boardSize
