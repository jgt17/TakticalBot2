from GameState import GameState


class TrainingGameState:
    def __init__(self, gameState, trainingScore):
        self.gameState = gameState
        self.trainingScore = trainingScore

    def generatePermutations(self):
        return [TrainingGameState(permuted, self.trainingScore)
                for permuted in self.gameState.generateNormalPermutations()] +\
               [TrainingGameState(permuted, -self.trainingScore)
                for permuted in self.gameState.generateInvertedPermutations()]

    def toNetworkInputs(self):
        return self.gameState.toNetworkInputs(), self.trainingScore

    def __str__(self):
        return str(self.trainingScore) + ": " + str(self.gameState)

    def __repr__(self):
        return repr(self.trainingScore) + ": " + repr(self.gameState)

