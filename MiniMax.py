from TakException import TakException


def __miniMaxHelper(gameState, depth, alpha, beta, player1):
    if gameState.flatBoard.winner != 2:
        return gameState.flatBoard.winner, ""
    elif depth == 0:
        return gameState.score(), ""

    moves = gameState.generateMoves()
    bestMove = moves[0]

    if player1:
        bestVal = -float("inf")
        for move in moves:
            try:
                nextState = gameState.applyMove(move)
                val, currentMove = __miniMaxHelper(nextState, depth - 1, alpha, beta, False)
            except TakException:
                val, currentMove = -float("inf"), ""
            if val > bestVal:
                bestVal = val
                bestMove = move
            alpha = max(alpha, bestVal)
            if beta <= alpha:
                break
        return bestVal, bestMove
    else:
        bestVal = float("inf")
        for move in moves:
            try:
                nextState = gameState.applyMove(move)
                val, currentMove = __miniMaxHelper(nextState, depth - 1, alpha, beta, True)
            except TakException:
                val, currentMove = float("inf"), ""
            if val < bestVal:
                bestVal = val
                bestMove = move
            alpha = max(alpha, bestVal)
            if beta <= alpha:
                break
        return bestVal, bestMove

def miniMax(gameState, depth = 2):
    player1 = (gameState.turnIndicator == 1)
    val, move = __miniMaxHelper(gameState, depth, -float("inf"), float("inf"), player1)
    return move
