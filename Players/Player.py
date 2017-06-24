from abc import ABC, abstractmethod


# abstract player class
class Player(ABC):

    def __init__(self, isWhitePlayer, playerName):
        self.isWhitePlayer = isWhitePlayer
        self.playerName = playerName

    # given a GameState, produces a moveSpecificationString
    # describing the move the player desires to make.
    # individual implementations are responsible for ensuring the returned move is valid
    @abstractmethod
    def getMove(self, board):
        raise NotImplementedError

    # used to notify the player that they won the game
    @abstractmethod
    def won(self):
        raise NotImplementedError

    # used to notify the player that they lost the game
    @abstractmethod
    def lost(self):
        raise NotImplementedError