# helper functions for changing between notation styles
# standard tak notation is PTN: https://www.reddit.com/r/Tak/wiki/portable_tak_notation
# the server uses it's own notation: https://github.com/chaitu236/TakServer/blob/master/README.md


# converts a move specificaton string from portable tak notation (PTN) to server notation
def toServerNotation(ptn):
    #todo
    pass


# converts a move specification string from server notation to PTN
def toPTN(serverNotation):
    # print(serverNotation)
    serverNotationParts = str.split(serverNotation)
    # print(serverNotationParts)
    if serverNotationParts[0] == "P":
        if len(serverNotationParts) > 2:
            if serverNotationParts[2] == "W":
                return "S" + str.lower(serverNotationParts[1])
            else:
                return "C" + str.lower(serverNotationParts[1])
        else:
            return str.lower(serverNotationParts[1])
    else:
        total = sum([int(n) for n in serverNotationParts[3:]])
        # moving left
        direction = "#"
        if serverNotationParts[1][0] < serverNotationParts[2][0]:
            direction = ">"
        elif serverNotationParts[1][0] > serverNotationParts[2][0]:
            direction = "<"
        elif serverNotationParts[1][1] < serverNotationParts[2][1]:
            direction = "+"
        elif serverNotationParts[1][1] > serverNotationParts[2][1]:
            direction = "-"
        dropCounts = ""
        for n in serverNotationParts[3:]:
            dropCounts += str(n)
        if total == 1:                                      # only one piece moved
            return str.lower(serverNotationParts[1]) + direction
        elif total == int(dropCounts):                      # all the pieces are place on the next square
            return str(total) + str.lower(serverNotationParts[1]) + direction
        else:
            return str(total) + str.lower(serverNotationParts[1]) + direction + dropCounts
