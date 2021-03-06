## DONOT CHANGE ANYTHING IN THIS FILE
'''
This method implements the popular snake game we all loved to play as kids:
You have a snake and a food source. The snake moves towards the food to eat it and
grows anytime it eats the food. In this implementation, the  snake can cross
boundaries and enter through the other ends.
'''
import random
import curses
import time
from movement import move

s = curses.initscr()
curses.start_color()
curses.curs_set(0)
sh, sw = s.getmaxyx()
w = curses.newwin(sh+1, sw+1, 0, 0)
w.keypad(1)
w.timeout(100)
maxScore = 0
scores = []
score = 0
snk_x = sw//4
snk_y = sh//2
snake = [
    [snk_y, snk_x],
    [snk_y, snk_x-1],
    [snk_y, snk_x-2],
    [snk_y, snk_x-3]
]

food = [sh//2, sw//2]
w.addch(food[0], food[1], curses.ACS_PI)

key = curses.KEY_RIGHT
color = random.randint(1,6)
curses.init_pair(1, color, curses.COLOR_WHITE)
curses.init_pair(2, 2, curses.COLOR_WHITE)
try:
    with open("high score","r") as f:
        scores = [int(i)  for j in f for i in j.strip().split(" ") if i.isdigit()]
        f.close()
except:
    print("File doesn't exist")
if len(scores) > 0:
    maxScore = max(scores)

while True:
    w.addstr(0, 2, 'Score : ' + str(score) + ' ',curses.color_pair(1))
    w.addstr(0, 20, 'High Score : ' + str(maxScore) + ' ',curses.color_pair(2))

    prevKey = key
    #Increases the speed of Snake as its length increases
    w.timeout(100 - (len(snake)//5 + len(snake)//10)%120)

    next_key = w.getch()
    key = key if next_key == -1 else next_key

    if key == ord(' '):          # If SPACE BAR is pressed, wait for another
        key = -1                 # one (Pause/Resume)
        while key != ord(' '):
            key = w.getch()
        key = prevKey
        continue
         # If an invalid key is pressed
    if key not in [ curses.KEY_LEFT, curses.KEY_RIGHT, curses.KEY_UP, curses.KEY_DOWN, 27]:
        key = prevKey
    new_head = [snake[0][0], snake[0][1]]
    move(key, new_head)
    snake.insert(0, new_head)

     # If snake crosses the boundaries, make it enter from the other side
    if snake[0][0] == 0: snake[0][0] = sh-1
    if snake[0][1] == 0: snake[0][1] = sw -1
    if snake[0][0] == sh: snake[0][0] = 1
    if snake[0][1] == sw: snake[0][1] = 1


    if snake[0] in snake[1:]:
        file = open('high score', 'a+')
        file.write(str(score) + '\n')
        file.close()
        time.sleep(1)
        curses.endwin()
        quit()

    if snake[0] == food:
        food = None
        score += 1
        while food is None:
            nf = [
                random.randint(1, sh-2),
                random.randint(1, sh-2)
            ]
            food = nf if nf not in snake else None
        w.addch(food[0], food[1], curses.ACS_PI)
    else:
        tail = snake.pop()
        w.addch(tail[0], tail[1], ' ')
    w.addch(snake[0][0], snake[0][1], curses.ACS_CKBOARD)
