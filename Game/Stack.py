from copy import copy

import numpy as np

from Game.TakException import TakException


class Stack:
    # class representing the the stack of pieces on a square of the board

    # ints for representing the pieces. Do not change these.
    __blackCapstone = -3  # can only be on top
    __blackStandingStone = -2  # can only be on top
    __blackFlatStone = -1
    __whiteFlatStone = 1
    __whiteStandingStone = 2  # can only be on top
    __whiteCapstone = 3  # can only be on top

    # carry limit
    # relies on only one size of game being played at once
    carryLimit = None

    def __init__(self, pieces=None, stack=None, carryLimit=5):
        self.__pieces = None

        if pieces is not None:
            self.__pieces = copy(pieces)
        elif stack is not None:
            self.__pieces = copy(stack.__peices)
        else:
            self.__pieces = []

        if Stack.carryLimit is None:
            Stack.carryLimit = carryLimit

    # add pieces to a stack, enforcing tak rules
    def place(self, number, stack=None):
        if stack is None:
            stack = Stack([number])
            number = 1

        if Stack.isCapstone(self.top()):
            raise TakException("Tried to place a " + str(stack) + " on top of " + str(self.__pieces))
        elif Stack.isStandingStone(self.top()):
            if stack.height() == 1 and Stack.isCapstone(stack.top()):
                self.flattenStandingStone()
                self.__pieces += stack.__pieces
            else:
                raise TakException("Tried to flatten a standing stone without a capstone")
        else:
            self.__pieces += stack.__pieces[:number]  # if a stack is given, remove the bottom "number"
            stack.__pieces = stack.__pieces[number:]  # from the stack and add them to this stack
            return stack                              # return the adjusted stack

    # remove pieces from a stack, then return the removed pieces
    # does not enforce carry limit
    def lift(self, number=1):
        if number > len(self.__pieces):
            raise TakException("Tried to pull " + str(number) + " pieces from " + str(self.__pieces))
        lifted = self.__pieces[-number:]
        self.__pieces = self.__pieces[:-number]
        return Stack(lifted)

    # returns the top piece on the stack, or 0 if the stack is empty
    def top(self):
        if len(self.__pieces) > 0:
            return self.__pieces[-1]
        else:
            return 0

    # returns the height of the stack
    def height(self):
        return len(self.__pieces)

    # flattens the standing stone at the top of a stack
    def flattenStandingStone(self):
        if Stack.isStandingStone(self.top()):
            self.__pieces[-1] = int(self.top() / 2)
        else:
            raise Exception("Tried to flatten a " + self.top())

    def countStones(self):
        whiteCount = 0
        blackCount = 0

        for piece in self.__pieces:
            if piece == 1 or piece == 2:
                whiteCount += 1
            elif piece == -1 or piece == -2:
                blackCount += 1

        return whiteCount, blackCount

    def __len__(self):
        return self.height()

    # returns false iff __pieces is empty
    def __bool__(self):
        return bool(self.__pieces)

    # returns an inverted version of the stack, swapping the players
    def invert(self):
        new = copy(self)
        new.__pieces = [-1 * piece for piece in new.__pieces]
        return new

    @staticmethod
    def isFlatStone(piece):
        return piece == Stack.__blackFlatStone or piece == Stack.__whiteFlatStone

    @staticmethod
    def isStandingStone(piece):
        return piece == Stack.__blackStandingStone or piece == Stack.__whiteStandingStone

    @staticmethod
    def isCapstone(piece):
        return piece == Stack.__blackCapstone or piece == Stack.__whiteCapstone

    def pieces(self):
        return self.__pieces

    def __str__(self):
        return self.toTPSString()

    def __repr__(self):
        return str(self.__pieces)

    def toTPSString(self):
        conv = {-1: "2", 1: "1", -2: "2S", 2: "1S", -3: "2C", 3: "1C"}
        return ''.join([conv[piece] for piece in self.__pieces])

    def toNetworkInputs(self):
        pieces = self.__pieces[-Stack.carryLimit:]
        pieces = [0] * (Stack.carryLimit + 1 - len(pieces)) + pieces
        inputs = np.zeros((len(pieces), 4))
        for i in range(len(pieces)):
            if pieces[i] != 0:
                # mark owner
                if pieces[i] > 0:
                    inputs[i, 0] = 1
                else:
                    inputs[i, 1] = 1
                # mark piece type
                piece = abs(pieces[i])
                if piece[i] == 1:
                    inputs[i, 2] = 1
                elif piece[i] == 2:
                    inputs[i, 3] = 1
                else:
                    # capstone is basically road and wall both, so makes sense to mark this way
                    inputs[i, 2:] = 1
        return np.packbits(inputs)
