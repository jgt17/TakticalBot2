import sqlite3

from DatabaseProcessing.databaseUtil import rawDatabaseFilename


# count the number of games with the appropriate board size and which did not end in resignation in the database
def countGames(boardSize=5):
    return executeSQL("SELECT count(*) FROM games\nWHERE size=" + str(boardSize) + " AND " +
                      "(result = \"R-0\" OR result = \"0-R\" OR result = \"F-0\" OR result = \"0-F\" " +
                      "OR result = \"1/2=1/2\")")[0][0]


# count the total number of moves in the filtered database
def countMoves(boardSize=5):
    return executeSQL("SELECT SUM(LENGTH(notation) - LENGTH(REPLACE(notation, ',', ''))+1) as numMoves " +
                      "FROM games\nWHERE size=" + str(boardSize) + " AND " +
                      "(result = \"R-0\" OR result = \"0-R\" OR result = \"F-0\" OR result = \"0-F\" " +
                      "OR result = \"1/2-1/2\")")[0][0]


# select the notation and result from games which did not result in a resignation
# format will be list of tuples
def filterGames(boardSize=5):
    return executeSQL("SELECT notation, result FROM games\nWHERE size=" + str(boardSize) + " AND " +
                      "(result = \"R-0\" OR result = \"0-R\" OR result = \"F-0\" OR result = \"0-F\" " +
                      "OR result = \"1/2=1/2\")" +
                      "\nlimit 0, 100")  # limit size for debugging todo remove limit


# load sql from a file to execute
# assumes sql is valid
def loadSQL(filename):
    sql = ""
    with open(filename) as f:
        line = f.readline()
        while line != "":
            sql += line + "\n"
            line = f.readline()
    return sql[:-1]  # remove trailing newline


# execute sql on the database
# assumes sql is valid
def executeSQL(sqlString):
    print("Executing sql")
    import os
    print(os.getcwd())
    print(rawDatabaseFilename)
    with sqlite3.connect("../" + rawDatabaseFilename) as connection:
        print("Opened db")
        cursor = connection.cursor()
        cursor.execute(sqlString)
        result = cursor.fetchall()
    print(result)
    return result


# load SQL from a file and execute it
def loadAndExecuteSQL(filename):
    executeSQL(loadSQL(filename))


# debugging
if __name__ == "__main__":
    print("starting")
    print(countGames(3))
