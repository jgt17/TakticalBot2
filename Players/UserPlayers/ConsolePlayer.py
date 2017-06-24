from Players.Player import Player


# class representing a user playing via the console
class ConsolePlayer(Player):

    def getMove(self, board):
        print(board)
        move = input(self.playerName + ", please enter your move using standard PTN notation: ")
        if not board.checkMove(move):
            while True:
                move = input(self.playerName + ", \"" + move + "\" is not a valid move. "
                                                               "Please enter a different move: ")
                if board.checkMove(move):
                    break
        return move

    def won(self):
        print(self.playerName + ", you won!")

    def lost(self):
        print(self.playerName + ", you lost.")
