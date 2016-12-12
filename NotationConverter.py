import string


# converts a move specificaton string from portable tak notation (PTN) to server notation
def toServerNotation(ptn):
    #todo
    pass


# converts a move specification string from server notation to PTN
def toPTN(serverNotation):
    serverNotationParts = str.split(serverNotation, " ")
    if serverNotationParts[0] == "P":
        if len(serverNotationParts) > 2:
            if serverNotationParts[2] == "W":
                return "S" + str.lower(serverNotationParts[1])
            else: return "C" + str.lower(serverNotationParts[1])
        else:
            return str.lower(serverNotationParts[1])
    else:
        total = sum([n for n in serverNotationParts[3:]])
        # moving left
        if serverNotationParts[1][0] > serverNotationParts[2][0]:
            direction = "<"
        elif serverNotationParts[1][0] > serverNotationParts[2][0]:
            direction = ">"
        elif serverNotationParts[1][1] > serverNotationParts[2][1]:
            direction = "<"
        elif serverNotationParts[1][1] > serverNotationParts[2][1]:
            direction = ">"
        dropCounts = ""
        for n in serverNotationParts[3:]:
            dropCounts += str(n)
        return total + serverNotationParts[1] + direction + dropCounts