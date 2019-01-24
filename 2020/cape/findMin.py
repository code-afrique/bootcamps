def findMinimum(list):  # find the minimum in the list
    current = list[0]
    for x in list:      # loop through all elements
        if (x < current):   # if statement
            current = x         # update current
    return current      # return current
min = findMinimum([4, 1, 6])        # assign
print("the minimum is \"{}\"".format(min))  # print
