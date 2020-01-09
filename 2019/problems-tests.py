"""

Implement the functions specified below.  Try to do as many as you
can as quickly as possible, so do the easiest ones first.  The
questions are not sorted by difficulty, so you need to guess which
are the easy and which are the hard problems.

Example:
    Write a function countEven(Lst) that returns the number of even entries in a Lst.
    Example: countEven([1,4,2,3,5]) should return 2.

Solution:
    def countEven(Lst):
        total = 0
        for x in Lst:
            if x % 2 == 0:
                total += 1
        return total

========================================================================

1. Write function checkRoots(a, b, c).
    This function checks the roots of a quadratic equation of the form
    ax^2 + bx + c = 0

    Tasks:
    1. First find the discriminant of the equation by using:
          discriminant = b*b - 4*a*c
    2. If the discriminant is > 0 return the string "different roots"
		Else if the discriminant is = 0 return string "equal roots"
		Else if the discriminant is < 0 return the string "complex roots"

    Hint: Use if-statements
    Example: checkRoots(1, 2, 1) should return "equal roots"
	##checkRoots(1, 1, 1) = "complex roots"
	##checkRoots(0, 1, 1) = "different roots"
	##checkRoots(1, 4, 4) = "equal roots"

2. Write function findMinimum(Lst).
    This function finds the minimum number in a list of numbers.  The function
    should return False if the list is empty.
    Hint: Keep track of the smallest entry you have seen.  Start with the first entry in the list.  Then loop through the remaining entries in the list to see if any are smaller.
    Example: findMinimum([2, 1, 3]) should return 1
	##findMinimum([]) == False
	##findMinimum([-1]) == -1
	##findMinimum([2, 1, 2]) == 1

3.  Write function robotReturnToOrigin(str).
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

	 ##robotReturnToOrigin("") == True
	 ##robotReturnToOrigin("LUDR") == True
	 ##robotReturnToOrigin("LUR") == False

4. Write a function findSecondHighestNumber(Lst).
    This function finds the second highest number in  a list of integers.  If the list has fewer
    than 2 numbers, the function should return False.
    Example: findSecondHighestNumber([3, 2, 5, 4, 1]) should return 4.
	##findSecondHighestNumber([1]) == False
	##findSecondHighestNumber([-1, -2]) == -2
	##findSecondHighestNumber([1, 3, -2, 4]) == 3

5. Write a function listOfEvenNumbers(start, end).
    This function returns a sorted list of even numbers starting from start (inclusive if even) and ending at end (exclusive).
    Example: listOfEvenNumbers(3, 9) should return [4, 6, 8].
	##listOfEvenNumbers(4, 4) == []
	##listOfEvenNumbers(-3, 4) == [-2, 0, 2]
	##listOfEvenNumbers(-2, 4) == [-2, 0, 2]

6. Write function isPalindrome(Lst).
    This function returns whether the given list is a palindrome.
    Example isPalindrome([1, 2, 3, 2, 1]) should return True.
	##isPalindrome([1, 2, 3]) == False
	##isPalindrome([]) == True
	##isPalindrome([1, 0, 1]) == True

7. Write function sign(i).
    This function returns -1 if i < 0, 0 if i == 0, and 1 if i > 0
    Example 1: sign(5) should return 1
    Example 2: sign(0) should return 0
    Example 3: sign(-2) should return -1
	##sign(-1) == -1
	##sign(0) == 0
	##sign(3.14) == 1

8. Write function isUpper(str).
     This function returns whether str is all upper case or not.
	 (You may assume the string only has letters in it.)
     Example: isUpper("ABC") should return True
	##isUpper("") == True
	##isUpper("Aa") == False
	##isUpper("AAAAAAAAAA") == True

9. Write function isAnagram(str1, str2) to check if two input strings form an anagram.
    That is, one string is a re-arrangement of the letters in the other word.
	Example: isAnagram("iceman", "cinema") == True
	##isAnagram("", "") == True
	##isAnagram("aabbcc", "bbccaa") == True
	##isAnagram("aabcc", "bbccaa") == False

10. Write function allUnique(str) that checks to see if all characters in the string
	are unique (i.e., do not appear more than once)..
	Example: allUnique("hello") == False
	##allUnique("") == True
	##allUnique("qwerty") == True
	##allUnique("abcc") == False

"""
