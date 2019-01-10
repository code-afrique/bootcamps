1. write function quadratic_fun(a, b, c).
	This function checks the roots of a quadratic equation of the form 
	ax^2 + bx + c = 0

	Tasks:
	1. First find the discriminant of the equation by using:
	 	 discriminant = b*b - 4*a*c
	2. If the discriminant is > 0 return the string 'real roots' 
			Else if the discriminant is = 0 return string 'equal roots'
	    Else if the discriminant is < 0 returnthe string 'complex roots'

	Hint: Use if-statements
	Example: quadratic_fun(1, 2, 1) should return 'equal roots"

2. write function find_minimum(lst).
	This function finds the minimum number in a list of numbers.
	Example: find_minimum([2, 1, 3]) should return 1

3. write function reverse(str).
	This function reverses the characters in a string.
	Example: reverse('hello') should return 'olleh'
	
4. There is a robot starting at position (0, 0), the origin, on a 2D plane.
    Given a sequence of its moves, judge if this robot ends up at (0, 0) after it completes its moves.
    The move sequence is represented by a string, and the character moves[i] represents its ith move.
    Valid moves are R (right), L (left), U (up), and D (down). 
    If the robot returns to the origin after it finishes all of its moves, return true. Otherwise, return false.
    
    Example 1:
    Input: "UD"
    Output: true 
    Explanation: The robot moves up once, and then down once. All moves have the same magnitude, so it ended up at the origin where it started. Therefore, we return true.
    
    Example 2:
    Input: "LL"
    Output: false
    Explanation: The robot moves left twice. It ends up two "moves" to the left of the origin. We return false because it is not at the origin at the end of its moves.



7. Write a function find_second_highest_number(lst).
	This function finds the second highest number in  a list of integers.

8. Write a function list_of_even_numbers(start, end).
	This function returns a list of even numbers starting from