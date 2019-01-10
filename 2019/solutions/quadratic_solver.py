"""A program to solve quadratic equations"""
from modules import math, check_solution, graph


def check_roots(a,b,c):
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
	return (x1, x2)

