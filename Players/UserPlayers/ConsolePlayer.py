from Players import Player


# class representing a user playing via the console
class ConsolePlayer(Player):

    def getMove(self, board):
        print(board)
        move = input(self.playerName + ", please enter your move using standard PTN notation: ")
        if not board.checkMove():
            while True:
                move = input(self.playerName + ", that move is not valid. Please enter a different move:")
                if board.checkMove():
                    break
