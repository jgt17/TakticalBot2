import copy
import string

from Game.MoveSpecification import MoveSpecification
from Game.Stack import Stack
from Game.FlatBoard import FlatBoard
from Game.TakException import TakException
from Misc import compositions
from Game import TakConstants


class GameState:
    # Class representing the state of the board
    # file is outer list, rank is inner list

    def __init__(self,
                 boardSize=5,
                 board=None,
                 turnCount=0):
        if board is None:
            board = [[Stack() for _ in range(boardSize)] for _ in range(boardSize)]
        self.board = board
        self.boardSize = len(board)
        self.turnCount = turnCount
        self.turnIndicator = turnCount % 2*-2+1       # 1 for white's turn, 0 for black's
        self.previousMoves = []

        whiteStonesOnBoard, blackStonesOnBoard = self.countStonesOnBoard()

        self.__whitePiecesPlayed = whiteStonesOnBoard
        self.whitePiecesRemaining = TakConstants.piecesAvailable[boardSize] - self.__whitePiecesPlayed

        self.__blackPiecesPlayed = blackStonesOnBoard
        self.blackPiecesRemaining = TakConstants.piecesAvailable[boardSize] - self.__blackPiecesPlayed

        self.__carryLimit = self.boardSize

        self.flatBoard = FlatBoard(self)
        self.pieceCounts = self.flatBoard.getPieceCounts()

        self.__whiteCapstonesAvailable = TakConstants.capstonesAvailable[boardSize] - self.pieceCounts[4]
        self.__blackCapstonesAvailable = TakConstants.capstonesAvailable[boardSize] - self.pieceCounts[4]

        self.score = 0

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
            if not new.__inBounds(file, rank):
                raise TakException("The location " + str(file) + "," + str(rank) + " is not on the board")
            position = new.board[file][rank]
            if position:
                raise TakException("Tried to place in " + str(file) + ", " + str(rank) + ", which is already occupied")
            else:
                # place for other player on first turn
                if new.turnCount >= 2:
                    position.place(toPlace * new.turnIndicator)
                else:
                    if abs(moveSpecification.whatToPlace) != 1:
                        print(self)
                        raise TakException("You must place a flatstone on the first turn: " + moveSpecificationString)
                    position.place(toPlace * new.turnIndicator * -1)
                if toPlace % 3 == 0 and new.turnIndicator == 1:
                    new.__whiteCapstonesAvailable -= 1
                elif toPlace % 3 == 0 and new.turnIndicator == -1:
                    new.__blackCapstonesAvailable -= 1
                elif new.turnIndicator == 1:
                    new.__whitePiecesPlayed += 1
                    new.whitePiecesRemaining -= 1
                else:
                    new.__blackPiecesPlayed += 1
                    new.blackPiecesRemaining -= 1
            new.previousMoves.append(moveSpecificationString)
        # movement moves
        else:
            file = moveSpecification.file
            rank = moveSpecification.rank
            toMove = moveSpecification.numberToMove
            direction = moveSpecification.direction
            dropCounts = moveSpecification.dropCounts
            if not new.__inBounds(file, rank):
                raise TakException("Tried to move from " + str(file) + "," + str(rank) + ", which is out of bounds")
            position = new.board[file][rank]
            if toMove > new.__carryLimit:
                raise TakException("Tried to move " + str(toMove) + " pieces, which is greater than the carry limit" +
                                   str(new.__carryLimit))
            elif toMove > len(position):
                raise TakException("Tried to move " + str(toMove) + " pieces, which is more than " +
                                   str(file) + "," + str(rank) + " has")
            elif position.top() * new.turnIndicator < 0:
                raise TakException("Tried to move " + str(file) + ", " + str(rank) + " which is not controlled by you")
            else:
                movingStack = position.lift(toMove)
                while dropCounts:
                    if direction == ">":
                        file += 1
                    elif direction == "<":
                        file -= 1
                    elif direction == "+":
                        rank += 1
                    elif direction == "-":
                        rank -= 1
                    else:
                        raise TakException("Invalid movement direction:", direction)
                    if not new.__inBounds(file, rank):
                        raise TakException("Cannot drop tiles onto " + str(file) + "," + str(rank) +
                                           ", it is off the board " + moveSpecificationString)
                    new.board[file][rank].place(dropCounts.pop(0), movingStack)
                new.previousMoves.append(moveSpecificationString)
        new.turnIndicator *= -1
        new.turnCount += 1
        return new

    # checks whether the move specified is valid for the current GameState
    # returns True/False and message explaining any violation (empty string if none)
    def checkMove(self, moveSpecificationString, isPTN=True):
        try:
            self.applyMove(moveSpecificationString, isPTN)
            return True
        except TakException as e:
            return False

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
        for i in range(self.boardSize):
            for j in range(self.boardSize):
                # if the space is empty
                if not self.board[i][j]:
                    locString = self.__toLocString(i, j)
                    # assumes there are more flatstones
                    placementMoves.append(locString)
                    if self.turnCount > 2:
                        placementMoves.append("S"+locString)
                        if (self.turnIndicator == 1 and self.__whiteCapstonesAvailable > 0)\
                                or (self.turnIndicator == -1 and self.__blackCapstonesAvailable > 0):
                            placementMoves.append("C"+locString)
        return placementMoves

    # fixme: currently generates illegal moves (later pruned during applyMove during minimax, so not a huge issue)
    def __generateMovementMoves(self):
        movementMoves = []
        # for each space on the board
        for i in range(self.boardSize):
            for j in range(self.boardSize):
                stack = self.board[i][j]
                # if the space is not empty and is controlled by the current player
                if stack and stack.top() * self.turnIndicator > 0:
                    for toMove in range(1, min(self.__carryLimit+1, stack.height()+1)):
                        arrangements = compositions[toMove-1]
                        for arr in arrangements:
                            if len(arr) <= i:
                                movementMoves.append(self.__moveStringGen(toMove, i, j, "<", arr))

                            if len(arr) <= self.boardSize - i - 1:
                                movementMoves.append(self.__moveStringGen(toMove, i, j, ">", arr))

                            if len(arr) <= j:
                                movementMoves.append(self.__moveStringGen(toMove, i, j, "-", arr))

                            if len(arr) <= self.boardSize - j - 1:
                                movementMoves.append(self.__moveStringGen(toMove, i, j, "+", arr))
        return movementMoves

    @staticmethod
    def __toLocString(i, j):
        return string.ascii_lowercase[i]+str(j+1)

    @staticmethod
    def __moveStringGen(toMove, i, j, directionSymbol, dropCounts):
        if toMove > 1:
            moveString = str(toMove) + GameState.__toLocString(i, j) + directionSymbol
            for n in dropCounts:
                moveString += str(n)
            return moveString
        else:
            return GameState.__toLocString(i, j) + directionSymbol

    # returns evaluation of the quality of the board for white
    def score(self):
        return self.score

    # returns data about the board in the appropriate format to feed to the CNN for training
    def toNetworkInputs(self):
        flatContents = []
        # row by col by stack + counts
        for i in range(self.boardSize):
            for j in range(self.boardSize):
                flatContents += self.board[j][i].toNetworkInputs()
        return bytes(flatContents), bytes(self.flatBoard.getPieceCounts())

    # returns data about the board in the appropriate format to feed the CNN for playing
    def toNetworkApplyInputs(self):
        # noinspection PyUnusedLocal
        contents = [[0 for i in range(self.boardSize)] for i in range(self.boardSize)]
        for i in range(self.boardSize):
            for j in range(self.boardSize):
                contents[i][j] = self.board[j][i].toNetworkInputs()
        return contents, self.pieceCounts

    # returns a list of all permutations of the board
    # for increasing training data
    # (robustness to orientation)
    def generatePermutations(self):
        return self.generateNormalPermutations() + self.generateInvertedPermutations()

    # returns a list of all non-inverted permutations of the board
    def generateNormalPermutations(self):
        return self.__allRotations() + self.__flipHorizontal().__allRotations()

    # returns a list of all inverted permutations of the board
    def generateInvertedPermutations(self):
        return self.__invert().__allRotations() + self.__invert().__flipHorizontal().__allRotations()

    def __allRotations(self):
        rotations = [self]
        for i in range(3):
            rotations.append(rotations[-1].__rotate())
        return rotations

    def __rotate(self):
        new = copy.deepcopy(self)
        new.board = [list(elem) for elem in list(zip(*new.board[::-1]))]
        return new

    def __flipHorizontal(self):
        new = copy.deepcopy(self)
        new.board = new.board[::-1]
        return new

    def __flipVertical(self):
        new = copy.deepcopy(self)
        new.board = [elem[::-1] for elem in new.board]
        return new

    def __invert(self):
        new = copy.deepcopy(self)
        new.board = [[stack.invert() for stack in file] for file in new.board]
        return new

    # returns a string representation of the board in Tak Positional System (TPS) notation
    # https://www.reddit.com/r/Tak/wiki/tak_positional_system
    def toTPS(self):
        rows = []
        for row in range(self.boardSize-1, -1, -1):
            emptyCounter = 0
            rowList = []
            for col in range(self.boardSize):
                stack = self.board[col][row]
                if not stack:    # if the stack is empty
                    emptyCounter += 1
                else:
                    if emptyCounter == 1:
                        rowList.append("x")
                    elif emptyCounter > 1:
                        rowList.append("x" + str(emptyCounter))
                    emptyCounter = 0
                    rowList.append(stack.toTPSString())
            if emptyCounter == 1:
                rowList.append("x")
            elif emptyCounter > 1:
                rowList.append("x" + str(emptyCounter))
            rows.append(rowList)
        return '/'.join([','.join(row) for row in rows])

    # returns a GameState from a TPS string
    @staticmethod
    def fromTPS(tpsString):
        # todo
        pass

    # counts the number of flatstones on the board, including those buried in stacks
    def countStonesOnBoard(self):
        whiteTotalCount = 0
        blackTotalCount = 0

        for file in self.board:
            for stack in file:
                w, b = stack.countStones()
                whiteTotalCount += w
                blackTotalCount += b

        return whiteTotalCount, blackTotalCount

    # checks if a location is on the board
    def __inBounds(self, file, rank):
        return 0 <= file < self.boardSize and 0 <= rank < self.boardSize

    def __str__(self):
        return self.toTPS()

    def __repr__(self):
        return str(self.board)
