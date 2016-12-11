from Stack import Stack
from MoveSpecification import MoveSpecification
from FlatBoard import FlatBoard
from Misc import compositions
import string
import copy


class GameState:
    # Class representing the state of the board
    # file is outer list, rank is inner list

    # stones available for each board size
    piecesAvailable = {3: 10, 4: 15, 5: 21, 6: 30, 7: 40, 8: 50}
    # capstones available for each board size
    capstonesAvailable = {3: 0, 4: 0, 5: 1, 6: 1, 7: 2, 8: 2}

    def __init__(self,
                 boardSize=5,
                 board=None,
                 turnCount=0):
        if board.isNone():
            board = [[Stack() for _ in range(boardSize)] for _ in range(boardSize)]
        self.__board = board
        self.boardSize = len(board)
        self.turnCount = turnCount
        self.turnIndicator = turnCount % 2*-2+1       # 1 for white's turn, 0 for black's
        self.previousMoves = []

        self.__whitePiecesPlayed = self.countWhiteStonesOnBoard()
        self.__whitePiecesRemaining = GameState.piecesAvailable[boardSize] - self.__whitePiecesPlayed
        self.__whiteCapstonesAvailable = self.countWhiteCapstonesOnBoard() - GameState.capstonesAvailable[boardSize]

        self.__blackPiecesPlayed = self.countBlackStonesOnBoard()
        self.__blackPiecesRemaining = GameState.piecesAvailable[boardSize] - self.__blackPiecesPlayed
        self.__blackCapstonesAvailable = self.countBlackCapstonesOnBoard() - GameState.capstonesAvailable[boardSize]

        self.__carryLimit = self.boardSize

    # applies a move, given a move specification string
    # enforces tak rules
    def applyMove(self, moveSpecificationString, isPTN=True):
        new = copy.deepcopy(self)
        moveSpecification = MoveSpecification(moveSpecificationString, isPTN)
        # placement moves
        if moveSpecification.isPlacementMove:
            file = moveSpecification.file
            rank = moveSpecification.rank
            toPlace = moveSpecification.whatToPlace
            position = new.__board[file][rank]
            if position:
                raise Exception("Tried to place in", file, ",", rank, ", which is already occupied")
            elif not new.__inBounds(file, rank):
                raise Exception("The location", file, ",", rank, "is not on the board")
            else:
                position.place(toPlace * new.turnIndicator)
                if toPlace % 3 == 0 and new.turnIndicator == 1:
                    new.__whiteCapstonesAvailable -= 1
                elif toPlace % 3 == 0 and new.turnIndicator == -1:
                    new.__blackCapstonesAvailable -= 1
                elif new.turnIndicator == 1:
                    new.__whitePiecesPlayed += 1
                    new.__whitePiecesRemaining -= 1
                else:
                    new.__blackPiecesPlayed += 1
                    new.__blackPiecesRemaining -= 1
            new.previousMoves.append(moveSpecificationString)
        # movement moves
        else:
            file = moveSpecification.file
            rank = moveSpecification.rank
            toMove = moveSpecification.numberToMove
            direction = moveSpecification.direction
            dropCounts = moveSpecification.dropCounts
            if not new.__inBounds(file, rank):
                raise Exception("Tried to move from (", file, ",", rank, "), which is out of bounds")
            position = new.__board[file][rank]
            if toMove > new.__carryLimit:
                raise Exception("Tried to move",
                                toMove,
                                "pieces, which is greater than the carry limit",
                                new.__carryLimit)
            elif toMove > len(position):
                raise Exception("Tried to move", toMove, "pieces, which is more than (", file, ",", rank, ") has")
            else:
                movingStack = position.lift(toMove)
                while dropCounts:
                    if direction == "+":
                        file += 1
                    elif direction == "-":
                        file -= 1
                    elif direction == ">":
                        rank += 1
                    elif direction == "<":
                        rank -= 1
                    else:
                        raise Exception("invalid movement direction:", direction)
                    if not new.__inBounds(file, rank):
                        raise Exception("Cannot drop tiles onto (", file, ",", rank, "), it is off the board")
                    new.__board[file][rank].place(dropCounts.pop(0), movingStack)
                new.previousMoves.append(moveSpecificationString)
        new.turnIndicator *= -1
        return new

    # checks whether a player has won
    # returns 1 if white won, -1 if black won, 0 if it is a draw, and 2 if the game isn't over
    def checkVictory(self):
        return FlatBoard(self).checkVictory()

    # returns a list of all possible moves
    def generateMoves(self):
        return self.__generatePlacementMoves() + self.__generateMovementMoves()

    # returns a list of all possible placement moves
    def __generatePlacementMoves(self):
        placementMoves = []
        for i in self.__board:
            for j in self.__board[i]:
                # if the space is empty
                if not self.__board[i][j]:
                    locString = self.__toLocString(i, j)
                    # assumes there are more flatstones
                    placementMoves.append(locString)
                    placementMoves.append("S"+locString)
                    if (self.turnIndicator == 1 and self.__whiteCapstonesAvailable > 0)\
                            or (self.turnIndicator == -1 and self.__blackCapstonesAvailable > 0):
                        placementMoves.append("C"+locString)
        return placementMoves

    def __generateMovementMoves(self):
        movementMoves = []
        # for each space on the board
        for i in self.__board:
            for j in self.__board[i]:
                stack = self.__board[i][j]
                # if the space is not empty and is controlled by the current player
                if stack and stack.top() * self.turnIndicator > 0:
                    for toMove in range(max(self.__carryLimit, stack.height())):
                        arrangements = compositions[toMove]
                        for arr in arrangements:
                            if len(arr) < i:
                                movementMoves.append(self.__moveStringGen(toMove, i, j, "<", arr))
                            if len(arr) < self.boardSize - i - 1:
                                movementMoves.append(self.__moveStringGen(toMove, i, j, ">", arr))
                            if len(arr) < j:
                                movementMoves.append(self.__moveStringGen(toMove, i, j, "-", arr))
                            if len(arr) < self.boardSize - j - 1:
                                movementMoves.append(self.__moveStringGen(toMove, i, j, "+", arr))
        return movementMoves

    @staticmethod
    def __toLocString(i, j):
        return string.ascii_lowercase[i]+str(j+1)

    @staticmethod
    def __moveStringGen(toMove, i, j, directionSymbol, dropCounts):
        moveString = str(toMove) + GameState.__toLocString(i, j) + directionSymbol
        for n in dropCounts:
            moveString += n
        return moveString

    # returns evaluation of the quality of the board for white
    def score(self):
        # todo
        self
        return 0

    # returns data about the board in the appropriate format to feed to the DANN
    def toNetworkInputs(self):
        # todo
        self
        return []

    # returns a list of all permutations of the board
    # for increasing training data
    # (robustness to orientation)
    def generatePermutations(self):
        permutations = self.__allRotations() + self.__flipHorizontal().__allRotations()
        inverted = self.__invert()
        permutations += inverted.__allRotations() + inverted.__flipHorizontal().__allRotations()
        return permutations

    def __allRotations(self):
        rotatations = [self.__rotate()]
        for i in range(3):
            rotatations.append(rotatations[-1].__rotate())

    def __rotate(self):
        new = copy.deepcopy(self)
        new.__board = [list(elem) for elem in list(zip(*new.__board[::-1]))]
        return new

    def __flipHorizontal(self):
        new = copy.deepcopy(self)
        new.__board = new.__board[::-1]
        return new

    def __flipVertical(self):
        new = copy.deepcopy(self)
        new.__board = [elem[::-1] for elem in new.__board]
        return new

    def __invert(self):
        new = copy.deepcopy(self)
        new.__board = [stack.invert() for file in new.__board for stack in file]
        return new

    # returns a string representation of the board in Tak Positional System (TPS) notation
    def toTPS(self):
        # todo
        pass

    # returns a GameState from a TPS string
    @staticmethod
    def fromTPS(tpsString):
        # todo
        pass

    # counts the number of white stones on the board
    def countWhiteStonesOnBoard(self):
        # todo
        self
        return 0

    # counts the number of black stones on the board
    def countBlackStonesOnBoard(self):
        # todo
        self
        return 0

    # counts the number of white capstones on the board
    def countWhiteCapstonesOnBoard(self):
        # todo
        self
        return 0

    # counts the number of black capstones on the board
    def countBlackCapstonesOnBoard(self):
        # todo
        return 0

    # counts the number of flatstones white has
    def countWhiteFlatstones(self):
        # todo
        return 0

    def countBlackFlatstones(self):
        # todo
        return 0

    # checks if a location is on the board
    def __inBounds(self, file, rank):
        return 0 <= file <= self.boardSize and 0 <= rank <= self.boardSize
