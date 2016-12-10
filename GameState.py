from Stack import Stack
from MoveSpecification import MoveSpecification


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
        self.__boardSize = len(board)
        self.__turnCount = turnCount
        self.__turnIndicator = turnCount % 2*-2+1       # 1 for white's turn, 0 for black's
        self.previousMoves = []

        self.__whitePiecesPlayed = self.countWhiteStonesOnBoard()
        self.__whitePiecesRemaining = GameState.piecesAvailable[boardSize] - self.__whitePiecesPlayed
        self.__whiteCapstonesAvailable = self.countWhiteCapstonesOnBoard() - GameState.capstonesAvailable[boardSize]

        self.__blackPiecesPlayed = self.countBlackStonesOnBoard()
        self.__blackPiecesRemaining = GameState.piecesAvailable[boardSize] - self.__blackPiecesPlayed
        self.__blackCapstonesAvailable = self.countBlackCapstonesOnBoard() - GameState.capstonesAvailable[boardSize]

        self.__carryLimit = self.__boardSize

    # applies a move, given a move specification string
    # enforces tak rules
    def applyMove(self, moveSpecificationString, isPTN=True):
        moveSpecification = MoveSpecification(moveSpecificationString, isPTN)
        # placement moves
        if moveSpecification.isPlacementMove:
            file = moveSpecification.file
            rank = moveSpecification.rank
            toPlace = moveSpecification.whatToPlace
            position = self.__board[file][rank]
            if position:
                raise Exception("Tried to place in", file, ",", rank, ", which is already occupied")
            elif not self.__inBounds(file, rank):
                raise Exception("The location", file, ",", rank, "is not on the board")
            else:
                position.place(toPlace*self.__turnIndicator)
            self.previousMoves.append(moveSpecificationString)
        # movement moves
        else:
            file = moveSpecification.file
            rank = moveSpecification.rank
            toMove = moveSpecification.numberToMove
            direction = moveSpecification.direction
            dropCounts = moveSpecification.dropCounts
            if not self.__inBounds(file, rank):
                raise Exception("Tried to move from (", file, ",", rank, "), which is out of bounds")
            position = self.__board[file][rank]
            if toMove > self.__carryLimit:
                raise Exception("Tried to move",
                                toMove,
                                "pieces, which is greater than the carry limit",
                                self.__carryLimit)
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
                    if not self.__inBounds(file, rank):
                        raise Exception("Cannot drop tiles onto (", file, ",", rank, "), it is off the board")
                    self.__board[file][rank].place(dropCounts.pop(0), movingStack)
                self.previousMoves.append(moveSpecificationString)
        self.__turnIndicator *= -1
        pass

    # checks whether a player has won returns 1 if white won, -1 if black won, and 0 if neither has won
    def checkVictory(self):
        # todo
        pass

    # returns a list of all possible moves
    def generateMoves(self):
        # todo
        pass

    # returns evalation of the quality of the board for white
    def score(self):
        # todo
        pass

    # returns data about the board in the appropriate format to feed to the DANN
    def toNetworkInputs(self):
        # todo
        pass

    # returns a list of all permutations of the board
    # for increasing training data
    # (robustness to orientation)
    def generatePermutations(self):
        # todo
        pass

    # returns a string representation of the board in Tak Positional System (TPS) notation
    def toTPS(self):
        # todo
        pass

    # returns a GameState from a TPS string
    @staticmethod
    def fromTPS(tpsString):
        # todo
        pass

    #counts the number of white stones on the board
    def countWhiteStonesOnBoard(self):
        # todo
        return 0

    #counts the number of black stones on the board
    def countBlackStonesOnBoard(self):
        # todo
        return 0

    #counts the number of white capstones on the board
    def countWhiteCapstonesOnBoard(self):
        # todo
        return 0

    #counts the number of black capstones on the board
    def countBlackCapstonesOnBoard(self):
        # todo
        return 0

    # checks if a location is on the board
    def __inBounds(self, file, rank):
        return 0 <= file <= self.__boardSize and 0 <= rank <= self.__boardSize