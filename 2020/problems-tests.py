Implement the functions specified below.  Try to do as many as you
can as quickly as possible, so do the easiest ones first.  The
questions are not sorted by difficulty, so you need to guess which
are the easy and which are the hard problems.

Keep all functions in the edit window and we will grade each one
when the contest is over.

Example 1:
	Write a function lastTwo(Lst) that returns the last two elements
	of a string or list.  You may assume that length of the list or
	string is at least 2.

Solution:
	def lastTwo(Lst):
		return Lst[len(Lst) - 2] + Lst[len(Lst) - 1]

Example 2:
    Write a function countEven(Lst) that returns the number of even entries in a Lst.
    Example: countEven([1,4,2,3,5]) should return 2.

Solution:
    def countEven(Lst):
        result = 0
        for x in Lst:
            if x % 2 == 0:
                result += 1
        return result

Handy examples of Python expressions:

	Numbers:  2, -3.14
	Strings:  "hello", "world"
	Lists:	  [ 1, 3, 0 ], [ ]
	Operators: +, -, *, /, //, %
	Built-in functions:	len(s) returns the length of s

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
    This function finds the minimum number in a list of numbers.  You may
	assume Lst is not an empty list.
    Hint: Keep track of the smallest entry you have seen.  Start with the
	first entry in the list.  Then loop through the remaining entries in
	the list to see if any are smaller.
    Example: findMinimum([2, 1, 3]) should return 1
	##findMinimum([-1]) == -1
	##findMinimum([2, 1, 2]) == 1

3.  Write function robotReturnToOrigin(str).
     There is a robot starting at position (0, 0), the origin, on a 2D plane.
     Given a sequence of its moves, judge if this robot ends up at (0, 0)
	 after it completes its moves.  The move sequence is represented by a
	 string, and the character moves[i] represents its ith move.
     Valid moves are R (right), L (left), U (up), and D (down).
     If the robot returns to the origin after it finishes all of its moves,
	 return the string "robot returns to origin". Otherwise, return the
	 string "robot does not return to origin".

     Example 1:
     Input: "UD"
     Output: "robot returns to origin"
     Explanation: The robot moves up once, and then down once. All moves
	 have the same magnitude, so it ended up at the origin where it started. 

     Example 2:
     Input: "LL"
     Output: "robot does not return to origin"
     Explanation: The robot moves left twice. It ends up two "moves" to
	 the left of the origin. Therefore, it is not at the origin at the end
	 of its moves.

	 ##robotReturnToOrigin("") == "robot returns to origin"
	 ##robotReturnToOrigin("LUDR") == "robot returns to origin"
	 ##robotReturnToOrigin("LUR") == "robot does not return to origin"

4. Write a function findSecondHighestNumber(Lst).
    This function finds the second highest number in a list of numbers.
	You may assume that the list has at least two elements in it.
    Example: findSecondHighestNumber([3, 2, 5, 4, 1]) should return 4.
	##findSecondHighestNumber([-1, -2]) == -2
	##findSecondHighestNumber([1, 3, -2, 4]) == 3

5. Write a function listOfEvenNumbers(start, end).
    This function returns a sorted list of even numbers starting from
	start (inclusive if even) and ending at end (exclusive).
    Example: listOfEvenNumbers(3, 9) should return [4, 6, 8].
	##listOfEvenNumbers(4, 4) == []
	##listOfEvenNumbers(-3, 4) == [-2, 0, 2]
	##listOfEvenNumbers(-2, 4) == [-2, 0, 2]

6. Write function checkPalindrome(Lst).
    This function returns the string "palindrome" if Lst is a palindrome,
	and the string "not palindrome" if it is not.  A palindrome is any
	sequence that reads the same forwards and backwards. e.g. "racecar"
	or [7, 3, 2, 2, 3, 7].  For example, isPalindrome([1, 2, 3, 2, 1])
	should return "palindrome".
	##isPalindrome([1, 2, 3]) == "not palindrome"
	##isPalindrome([]) == "palindrome"
	##isPalindrome([1, 0, 1]) == "palindrome"

7. Write function sign(i).
    This function returns -1 if i < 0, 0 if i == 0, and 1 if i > 0
    Example 1: sign(5) should return 1
    Example 2: sign(0) should return 0
    Example 3: sign(-2) should return -1
	##sign(-1) == -1
	##sign(0) == 0
	##sign(3.14) == 1

8. Write function fff(x, y) that returns the square of x plus the square
	of y.
     Example: fff(2, 3) should return 13 (because 4 + 9 is 13)
	##fff(0, 0) == 0
	##fff(2, 0) == 4
	##fff(0, -3) == 9

9. Write function isAnagram(str1, str2) to check if two input strings form
    an anagram.  That is, one string is a re-arrangement of the letters in
	the other word. Return the string "anagram" if the strings are anagrams.
    Otherwise, return "not anagram".
	Example: isAnagram("iceman", "cinema") == "anagram"
	##isAnagram("", "") == "anagram"
	##isAnagram("aabbcc", "bbccaa") == "anagram"
	##isAnagram("aabcc", "bbccaa") == "not anagram"

10. Write function allUnique(str) that checks to see if all characters in
    the string are unique (i.e., do not appear more than once). Return the
	string "all unique" if they are all unique. Otherwise, return the
	string "not all unique"
	Example: allUnique("hello") == "not all unique"
	##allUnique("") == "all unique"
	##allUnique("qwerty") == "all unique"
	##allUnique("abcc") == "not all unique"
