"""
Created by Jesse Phillips on January 3, 2019

Module which contains some helper functions for Tic-Tac-Toe-Python

"""

from game2d import *
GAME_WIDTH = 800
GAME_HEIGHT = 600

def newLine(x1, y1, x2, y2):
    """ Helper function to create a line on the canvas starting at point (x1,y1)
    and ending at point (x2, y2)
    
    """
    
    return GPath(points = [x1, y1, x2, y2],
                            linewidth = 2, linecolor = 'black')


# Students will be responsible for implementing the function below

def createGridLines():
    """ Helper function to create the tic tac toe grid lines """
    
    # YOUR CODE GOES HERE
    result = []
    result.append(newLine(0, GAME_HEIGHT/3, GAME_WIDTH, GAME_HEIGHT/3))
    result.append(newLine(0, 2*GAME_HEIGHT/3, GAME_WIDTH, 2*GAME_HEIGHT/3))
    result.append(newLine(GAME_WIDTH/3, 0, GAME_WIDTH/3, GAME_HEIGHT))
    result.append(newLine(2*GAME_WIDTH/3, 0, 2*GAME_WIDTH/3, GAME_HEIGHT))
    return result