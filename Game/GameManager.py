from Game import TakConstants
from Game.GameState import GameState
from Players.UserPlayers.ConsolePlayer import ConsolePlayer


class GameManager:
    roundsLimit = 100000

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
        status = TakConstants.ongoing
        for i in range(GameManager.roundsLimit):
            move = self.whitePlayer.getMove(self.board)
            self.history.append(move)
            self.board = self.board.applyMove(move)

            status = self.board.checkVictory()
            if status != TakConstants.ongoing:
                break

            move = self.blackPlayer.getMove(self.board)
            self.history.append(move)
            self.board = self.board.applyMove(move)

            status = self.board.checkVictory()
            if status != TakConstants.ongoing:
                break

        if status == TakConstants.ongoing:
            status = TakConstants.overRounds

        if status == TakConstants.whiteWon:
            self.whitePlayer.won()
            self.blackPlayer.lost()
        elif status == TakConstants.blackWon:
            self.whitePlayer.lost()
            self.blackPlayer.won()
        else:
            self.whitePlayer.draw()
            self.blackPlayer.draw()

        return self.board, self.history, status


if __name__ == "__main__":
    GameManager(ConsolePlayer(True, "White"), ConsolePlayer(False, "Black")).playGame()
