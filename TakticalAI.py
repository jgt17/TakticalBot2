from GameState import GameState
from MiniMax import miniMax
from TakException import TakException


def playTak():
    currentGameState = GameState()
    print(currentGameState)

    while True:
        try:
            if currentGameState.turnIndicator == 1:
                move = miniMax(currentGameState)
                print("TakticalBot: "+move)
            else:
                move = input("Player:      ")
                if move == "quit":
                    break
            currentGameState = currentGameState.applyMove(move)
            print(currentGameState)
            winner = currentGameState.checkVictory()
            if winner != 2:
                if winner == 1:
                    print("TakticalBot Won!")
                elif winner == -1:
                    print("You Won!")
                else:
                    print("It was a draw")
        except TakException as exception:
            print(exception)
            continue

playTak()
