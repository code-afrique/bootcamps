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
    result = []

    #example code for you
    result.append(newLine(0, GAME_HEIGHT/3, GAME_WIDTH, GAME_HEIGHT/3)) 
    #the above code draws the first box

    #Hint: draw the remaining 8 squares.

    