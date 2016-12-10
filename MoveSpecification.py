import string

class MoveSpecification:

    pieceLetterToNumber = {"F": 1, "S": 2, "C": 3}

    fileLetterToIndex = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7,}
    directionIndicators = ["+", "-", ">", "<"]

    def __init__(self, moveSpecificationString, isPTN=True):
        if not isPTN:
            moveSpecificationString = self.toPTNFromServer(moveSpecificationString)
        # if the move is a movement move
        if any(direction in moveSpecificationString for direction in self.directionIndicators):
            # if the number to move is left unspecified
            if moveSpecificationString[0] in string.ascii_letters:
                self.isPlacementMove = False
                self.numberToMove = 1
                self.file = self.fileLetterToIndex[moveSpecificationString[0]]
                self.rank = int(moveSpecificationString[1])-1
                self.direction = moveSpecificationString[2]
                self.drops = [1]
            # if the number to move is specified
            else:
                if moveSpecificationString[-1 not in string.digits]:
                    moveSpecificationString = moveSpecificationString[:-1]
                self.isPlacementMove = False
                self.numberToMove = int(moveSpecificationString[0])
                self.file = self.fileLetterToIndex[moveSpecificationString[1]]
                self.rank = int(moveSpecificationString[2]) - 1
                self.direction = moveSpecificationString[3]
                self.dropCounts = []
                for num in moveSpecificationString[4:]:
                    self.dropCounts.append(int(num))
        # if the move is a placement move
        else:
            # if the piece is specified
            if moveSpecificationString[0] in ["F", "S", "C"]:
                self.isPlacementMove = True
                self.whatToPlace = self.pieceLetterToNumber[moveSpecificationString[0]]
                self.file = self.fileLetterToIndex[moveSpecificationString[1]]
                self.rank = int(moveSpecificationString[2]) - 1
            # if not, assume flatstone
            else:
                self.isPlacementMove = True
                self.whatToPlace = self.pieceLetterToNumber["F"]
                self.file = self.fileLetterToIndex[moveSpecificationString[0]]
                self.rank = int(moveSpecificationString[1]) - 1


    # converts a move from Server notation to PTN
    @staticmethod
    def toPTNFromServer(moveString):
        #todo
        return moveString


    # converts a move from PTN to Server notation
    @staticmethod
    def toServerFromPTN(movestring):
        #todo
        return movestring

