"""A program to solve quadratic equations"""
from modules import math, print_step_by_step, graph


def check_roots(a,b,c):
	"""
	This function checks the  roots of a quadratic equation of the form 
	ax^2 + bx + c = 0

	Task:
	1. First find the discriminant of the equation by using:
	 	 discriminant = b*b - 4*a*c
	2. If the discriminant is > 0 return the phrase 'real roots' 
			Else if the discriminant is = 0 return phrase 'equal roots'
	    Else if the discriminant is < 0 returnthe phrase 'complex roots'
	3. Return the discriminant

	Hint: Use if-statements
	"""
	
	#step 1 //TODO
	discriminant = 0 #replace 0 with your own code

	#step 2: //TODO

	#step 3 //TODO
	#return discriminant



def solve(a,b,c):
	"""
	This method solves a quadratic equation using the quadratic formula.
	A quadratic equation is one of the form: ax^2 + bx + c = 0

	Requirements:
	a: integer
	b: integer
	c: integer

	Hint: Use the quadratic formula.  You may also learn from how we found the 
				discriminant above

	Tasks: 
	1: Find the discriminant
	
	2. Compute the two roots, x1 and x2 by using the quadratic formula.  For eg.
			x1 = (-b + math.sqrt(discriminant)/(2*a)

	3. Print the step by step solution.
		Hint: Use the function called print_step_by_step

	4. Draw the graph of the equation
		Hint: use the function called graph

	5. return the value (x1,x2) as your answer
	"""

	#step 1 //TODO
	discriminant = 0 #replace 0 with your own code

	#step 2 //TODO
	x1 = 0 #replace 0 with your own code
	x2 = 0 #replace 0 with your own code

	#step 3 //TODO

	#step 4 //TODO

	#step 5
	discriminant = b**2 - 4.0*a*c
	x1 = (-b - math.sqrt(discriminant)) / (2.0*a)
	x2 = (-b + math.sqrt(discriminant)) / (2.0*a)
	return (x1,x2)

