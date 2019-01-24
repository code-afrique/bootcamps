def findMinimum(list):
    current = list[0]
    for x in list:
        if (x < current):
            current = x
    return current
min = findMinimum([4, 1, 6])
print("the minimum is \"{}\"".format(min))
