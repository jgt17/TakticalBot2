from GameState import GameState

class GameManager:

    def __init__(self,
                 whitePlayer,
                 blackPlayer,
                 boardSize=5):
        self.board = GameState(boardSize)
        self.whitePlayer = whitePlayer
        self.blackPlayer = blackPlayer
        self.history = list()

    def setWhitePlayer(self, newPlayer):
        self.whitePlayer = newPlayer

    def setBlackPlayer(self, newPlayer):
        self.blackPlayer = newPlayer

    def playGame(self):
        move = self.whitePlayer.getMove(self.board)
        self.history.append(move)
        self.board.applyMove()

        status = self.board.checkVictory()
        if status != GameState.ongoing:
            return self.board, self.history, status

        move = self.blackPlayer.getMove(self.board)
        self.history.append(move)
        self.board.applyMove()

        status = self.board.checkVictory()
        if status != GameState.ongoing:
            return self.board, self.history, status