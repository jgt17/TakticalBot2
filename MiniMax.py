from TakException import TakException

import numpy as np


def __miniMaxHelper(gameState, tfSession, inferenceOp, boardPH, pieceCountPH, depth, alpha, beta, player1):
    if gameState.flatBoard.winner != 2:
        return gameState.flatBoard.winner, ""
    elif depth == 0:
        return gameState.score, ""

    # generate next gameStates
    moves = gameState.generateMoves()
    nextStates = []
    for move in moves:
        try:
            nextStates.append(gameState.applyMove(move))
        except TakException:
            pass  # the move is illegal, don't consider it

    # get scores using CNN
    boards, pieceCounts = zip(*[gameState.toNetworkApplyInputs() for gameState in nextStates])
    scores = tfSession.run(inferenceOp, feed_dict={boardPH: boards, pieceCountPH: pieceCounts})
    for i in range(len(nextStates)):
        nextStates[i].score = np.asscalar(scores[i])
    bestMove = nextStates[0].previousMoves[-1]

    if player1:
        bestVal = -float("inf")
        for nextState in nextStates:
            try:
                val = max(nextState.score, __miniMaxHelper(nextState, tfSession,
                                                           inferenceOp, boardPH, pieceCountPH,
                                                           depth - 1, alpha, beta, False)[0])
            except TakException:
                val, currentMove = -float("inf"), ""
            if val > bestVal:
                bestVal = val
                bestMove = nextState.previousMoves[-1]
            alpha = max(alpha, bestVal)
            if beta <= alpha:
                break
        return bestVal, bestMove
    else:
        bestVal = float("inf")
        for nextState in nextStates:
            try:
                val = min(nextState.score, __miniMaxHelper(nextState, tfSession,
                                                           inferenceOp, boardPH, pieceCountPH,
                                                           depth - 1, alpha, beta, True)[0])
            except TakException:
                val, currentMove = float("inf"), ""
            if val < bestVal:
                bestVal = val
                bestMove = nextState.previousMoves[-1]
            beta = min(beta, bestVal)
            if beta <= alpha:
                break
        return bestVal, bestMove


def miniMax(gameState, tfSession, inferenceOp, boardPH, pieceCountPH, depth=3):
    player1 = (gameState.turnIndicator == 1)
    val, move = __miniMaxHelper(gameState, tfSession, inferenceOp, boardPH, pieceCountPH,
                                depth, -float("inf"), float("inf"), player1)
    return move
