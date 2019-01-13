"""

1. Write function checkRoots(a, b, c).
	This function checks the roots of a quadratic equation of the form
	ax^2 + bx + c = 0

	Tasks:
	1. First find the discriminant of the equation by using:
	 	 discriminant = b*b - 4*a*c
	2. If the discriminant is > 0 return the string "different roots"
			Else if the discriminant is = 0 return string "equal roots"
	    Else if the discriminant is < 0 returnthe string "complex roots"

	Hint: Use if-statements
	Example: checkRoots(1, 2, 1) should return 'equal roots"

2. Write function findMinimum(lst).
	This function finds the minimum number in a list of numbers.  The function
	should return False if the list is empty.
	Example: findMinimum([2, 1, 3]) should return 1

3. Write function reverse(str).
	This function reverses the characters in a string.
	Example: reverse('hello') should return 'olleh'

4.  Write function robotReturnToOrigin(str).
     There is a robot starting at position (0, 0), the origin, on a 2D plane.
     Given a sequence of its moves, judge if this robot ends up at (0, 0) after it completes its moves.
     The move sequence is represented by a string, and the character moves[i] represents its ith move.
     Valid moves are R (right), L (left), U (up), and D (down).
     If the robot returns to the origin after it finishes all of its moves, return True. Otherwise, return False.


     Example 1:
     Input: "UD"
    Output: True
    Explanation: The robot moves up once, and then down once. All moves have the same magnitude, so it ended up at the origin where it started. Therefore, we return True.

     Example 2:
     Input: "LL"
     Output: False
     Explanation: The robot moves left twice. It ends up two "moves" to the left of the origin. We return False because it is not at the origin at the end of its moves.

5. Write a function findSecondHighestNumber(lst).
	This function finds the second highest number in  a list of integers.  If the list has fewer
	than 2 numbers, the function should return False.
	Example: findSecondHighestNumber([3, 2, 5, 4, 1]) should return 4.

6. Write a function listOfEvenNumbers(start, end).
	This function returns a list of even numbers starting from start (inclusive if even) and ending at end
	(exclusive).
	Example: listOfEvenNumbers(3, 9) should return [4, 6, 8].

7. Write function doubleList(lst).
	This function doubles every number in a list of numbers.
	Example: doubleList([2, 1, 3]) should return [4, 2, 6].

8. Write function isPalindrome(lst).
	This function returns whether the given list is a palindrome.
	Example isPalindrome([1, 2, 3, 2, 1]) should return True.

9. Write function alternates(lst).
	This function returns True iff the function has alternatingly smaller and larger numbers.
	Example 1: alternates([1, 5, 3, 4, 2, 6]) should return True.
	Example 2: alternates([5, 3, 4, 2, 6]) should return True.
	Example 3: alternates([5, 3, 4, 5, 2]) should return False.

10. Write function nOccurrences(str1, str2).
	 This function returns how many times str2 occurs in str1.
	 Example nOccurrences('xxxx', 'xx') should return 3.

"""