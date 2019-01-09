"""A program to solve quadratic equations"""
from modules import math, check_solution, graph


def check_roots(a,b,c):
	"""
	This function checks the  roots of a quadratic equation of the form 
	ax^2 + bx + c = 0

	Task:
	1. First find the discriminant of the equation by using:
	 	 discriminant = b*b - 4*a*c
	2. If the discriminant is > 0 print out the phrase 'real roots'
	3. If the discriminant is = 0 print out the phrase 'equal roots'
	4. If the discriminant is < 0 print out the phrase 'complex roots'

	Hint: Use if-statements
	"""

	discriminant = 0 #replace 0 with your own code

	#solution
	discriminant = b**2 - 4*a*c
  
	if discriminant > 0:
		return "real roots"

	elif discriminant == 0:
		return "equal roots"

	else:
		return "complex roots"




def solve(a,b,c):
	"""
	Prints the two solutions of the quadratic equation ax^2 + bx + c = 0
	Requirements:
	a: integer
	b: integer
	c: integer

	Instructions: 
	step 1: Use the quadratic formula to compute the two solutions x1 and x2
			eg. x1 = (-b + math.sqrt(b**2 - 4*a*c)/(2*a)
	step 2: Now that you have x1 and x2 use the print_step_by_step function
			to print out the solution using factorization method.
			eg. 
			if x1 = -1 and x2 = 5
			print_step_by_step(x1,x2)
	"""
  
	#solution
	discriminant = b**2 - 4.0*a*c
	x1 = (-b - math.sqrt(discriminant)) / (2.0*a)
	x2 = (-b + math.sqrt(discriminant)) / (2.0*a)

	#Do not touch anything below this line:
	check_solution(a,b,c,x1,x2)
	

