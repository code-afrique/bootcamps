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


# Implement the function below

def createGridLines():
    """ Helper function to create the tic tac toe grid lines """
    
    # YOUR CODE GOES HERE
    