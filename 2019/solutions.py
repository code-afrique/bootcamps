"""Solutions to Hackathon Questions """
def check_roots(a,b,c):
	"""
	This method solves a quadratic equation using the quadratic formula.
	A quadratic equation is one of the form: ax^2 + bx + c = 0

	Requirements:
	a: integer
	b: integer
	c: integer
	"""
	

	discriminant = 0 #replace 0 with your own code

	#solution
	discriminant = b**2 - 4*a*c
  
	if discriminant > 0:
		return 1

	elif discriminant == 0:
		return 0

	else:
		return -1

#Solution for question 2:
def find_minimum(lst):
    if lst==[]:
        return False

    x = lst[0]

    for i in range(1,len(lst)):
        if lst[i] < x:
            x = lst[i]

    return x

#Solution for question 3:
def reverse(str):

    n = len(str)
    x=""
    for i in range(n-1,-1,-1):
        x += str[i]
    return x

#Solution for question 4:
def robot_return_to_origin(str):

    x = y = 0

    for move in str:
        if move == 'U': y -= 1
        elif move == 'D': y += 1
        elif move == 'L': x -= 1
        elif move == 'R': x += 1

    return x == y == 0

#Solution for question 5:
def find_second_highest_number(lst):

    if len(lst) < 2:
        return False

    largest = lst[0]
    largest2 = lst[0]

    for item in lst:
        if item > largest:
            largest = item
        elif largest2!=largest and largest2 < item:
                largest2 = item

    return largest2

#Solution for question 6:
def list_of_even_numbers(start, end):

    result = []
    for i in range(start,end):
        if i % 2 == 0:
            result.append(i)

    return result

#Solution for question 7:
def doubleList(lst):

    for i in range(len(lst)):
        lst[i]*= 2

    return lst

#Solution for question 8:
def isPalindrome(lst):

    if len(lst)<2:
        return True
    return (lst[0]==lst[-1]) and isPalindrome(lst[1:-1])

#Solution for question 9:
def alternates(lst):

    dir = lst[0] > lst[1]

    for i in range(len(lst)-1):
        if dir:
            if not (lst[i] > lst[i+1]):
                return False
        else:
            if not (lst[i] < lst[i+1]):
                return False

        dir = not dir

    return True

#Solution for question 10:
def nOccurrences(str1, str2):

    result = 0
    for i in range(len(str1)):
        if str1[i:i+len(str2)] == str2:
            result+=1

    return result
