import numpy as np
from mapGenerator import MapManager

def solve(square):

    result = set()
    
    def getValue(square):
        return square.number - np.sum(square.surrounding("flagged"))
    
    def possible_mines(square):
        possibleMines = np.empty(0, dtype=bool)
        for otherSquare in square.surroundingSquares:
            if otherSquare:
                if getattr(otherSquare, "covered") and not getattr(otherSquare, "flagged"):
                    possibleMines = np.append(possibleMines, True)
                else:
                    possibleMines = np.append(possibleMines, False)
            else:
                possibleMines = np.append(possibleMines, False)
        return possibleMines
    
    def squares_in_area(squares:np.ndarray, area:np.ndarray):
        for square in squares:
            if square not in area:
                return False
        return True
    
    def flag_squares(square):
        possibleMines = possible_mines(square)
        if np.sum(possibleMines) == 0:
            MapManager.edges.remove(square.cords)
            return
        square.altUncover()
        value = getValue(square)
        if np.sum(possibleMines) == value:
            for idx in np.where(possibleMines)[0]:
                square.surroundingSquares[idx].flag()
            MapManager.edges.remove(square.cords)
        else:
            possibleMines = square.surroundingSquares[possibleMines]
            for otherSquare in square.surroundingSquares[square.surrounding("number")]:
                otherValue = getValue(otherSquare)
                if otherValue < value:
                    otherPossibleMines = otherSquare.surroundingSquares[possible_mines(otherSquare)]
                    localPossibleMines = np.copy(possibleMines)
                    for covered in possibleMines:
                        if covered in otherPossibleMines:
                            localPossibleMines = np.delete(localPossibleMines, *np.where(localPossibleMines == covered))
                    if len(localPossibleMines) == value - otherValue:
                        for mine in localPossibleMines:
                            result.add((mine, 0))

    def uncover_squares(square):
        square.altUncover()
        if square.cords in MapManager.edges:
            value = getValue(square)
            possibleMines = square.surroundingSquares[possible_mines(square)]
            for otherSquare in square.surroundingSquares[square.surrounding("number")]:
                otherValue = getValue(otherSquare)
                if otherValue == value:
                    localPossibleMines = np.copy(possibleMines)
                    otherPossibleMines = otherSquare.surroundingSquares[possible_mines(otherSquare)]
                    if squares_in_area(otherPossibleMines, localPossibleMines):
                        for otherPossibleMine in otherPossibleMines:
                            localPossibleMines = np.delete(localPossibleMines, np.where(localPossibleMines == otherPossibleMine)[0])
                        for squareToUncover in localPossibleMines:
                            result.add((squareToUncover, 1))

    flag_squares(square)
    uncover_squares(square)
    return result
