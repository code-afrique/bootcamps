'''
This method implements the popular snake game we all use to play as kids:
You have a snake and a food. The snake moves towards the food to eat it and
grows anytime it eats the food.
You are responsible for implementing code that conntrols the
navigation of the snake. That is, if the up key is pressed, the snake should
move, if the down key is pressed, it should move down etc.
You're given an given the variable "key", which is the key that the user pressed
on the keyboard, and new_head which is the current position of the snake.

Structure of new_head:
Increase new_head[0] by one if you want to down and decrease by one if you
want to go up.
Increase  new_head[1] by one if you want to right and decrease by one if you
want to go left.
'''

import curses
KEY_DOWN = curses.KEY_DOWN
KEY_UP = curses.KEY_UP
KEY_LEFT = curses.KEY_LEFT
KEY_RIGHT = curses.KEY_RIGHT

### Students are responsible for implementing this method
def move(key, new_head):
    if key == KEY_DOWN:
        new_head[0] += 1
    if key == KEY_UP:
        new_head[0] -= 1
    if key == KEY_LEFT:
        new_head[1] -= 1
    if key == KEY_RIGHT:
        new_head[1] += 1
