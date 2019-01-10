#Solution for question 4:
def robot_return_to_origin(str):

    x = y = 0

    for move in str:
        if move == 'U': y -= 1
        elif move == 'D': y += 1
        elif move == 'L': x -= 1
        elif move == 'R': x += 1

    return x == y == 0


#Solution for question 2:
def find_minimum(lst):

    x = lst[0]

    for i in range(1,len(lst)):
        if lst[i] < x:
            x = lst[i]
            
    return x
