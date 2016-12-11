# for determining end-of-game, only the top stones on each stack matter
# this is a flattened version of the board containing only those pieces
# making it easier to find win conditions


class FlatBoard:

    def __init__(self, gameState):
        self.flatBoard = [[0 for _ in range(gameState.boardSize)] for _ in range(gameState.boardSize)]
        self.whitePiecesLeft = gameState.__whitePiecesRemaining
        self.blackPiecesLeft = gameState.__blackPiecesRemaining
        self.turnIndicator = gameState.__turnIndicator
        self.boardSize = gameState.boardSize
        for i in range(gameState.boardSize):
            for j in range(gameState.boardSize):
                self.flatBoard[i][j] = gameState.__board[i][j].top()

    def checkVictory(self):
        r = self.__checkRoadVictory()
        if r != 0:
            return r
        elif self.blackPiecesLeft == 0 or self.whitePiecesLeft == 0 or self.__boardIsCovered():
            return self.__checkFlatVictory()
        else:
            return 2

    def __checkRoadVictory(self):
        boardSize = len(self.flatBoard)
        leftEdge = set()
        bottomEdge = set()
        for i in range(boardSize):
            leftEdge.add((0, i))
            bottomEdge.add((i, 0))
        if self.__roadExists(leftEdge, boardSize, "horizontal", 1)\
                or self.__roadExists(bottomEdge, boardSize, "vertical", 1):
            return 1
        elif self.__roadExists(leftEdge, boardSize, "horizontal", -1)\
                or self.__roadExists(bottomEdge, boardSize, "vertical", -1):
            return -1
        else:
            return 2

    def __checkFlatVictory(self):
        whiteCount = 0
        blackCount = 0

        for file in self.flatBoard:
            for piece in file:
                if piece == 1:
                    whiteCount += 1
                elif piece == -1:
                    blackCount += 1

        if whiteCount > blackCount:
            return 1
        elif blackCount > whiteCount:
            return -1
        else:
            return 0

    def __boardIsCovered(self):
        for file in self.flatBoard:
            for piece in file:
                if piece == 0:
                    return False
        return True

    def __roadExists(self, openset, size, direction, player):
        closedSet = {}
        openSet = openset.copy()
        while openSet:
            curr = openSet.pop()
            if (direction == "horizontal" and curr[0] == size) or (direction == "vertical" and curr[1] == size):
                return True
            curr.add(closedSet)
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
        if self.__inBounds(i, j - 1):
            adj.add((i, j - 1))
        return adj

    def __inBounds(self, file, rank):
        return 0 <= file <= self.boardSize and 0 <= rank <= self.boardSize
