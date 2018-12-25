"""A program to solve quadratic equations"""
import math
import matplotlib.pyplot as plt

def solve(a,b,c):
	"""
	Prints the two solutions of the quadratic equation ax^2 + bx + c = 0
	Requirements:
	a: integer
	b: integer
	c: integer

	Instructions: 
	step 1: Use the quadratic formula to compute the two solutions x1 and x2
			eg. x1 = (-b + math.sqrt(b**2 - 4*a*c)/2a
	step 2: Now that you have x1 and x2 use the print_step_by_step function
			to print out the solution using factorization method.
			eg. 
			x1 = -1
			x2 = 5
			print_step_by_step(x1,x2)
	"""
	pass




###### DO NOT MODIFY ANYTHING BELOW THIS ############
def print_step_by_step(x1,x2):
	""" 
	Prints out the step by step solution given the two solutions to a quadratic equation.

	x^2+3x+2=0
	x^2+2x + x+2= 0
	x(x+2) + 1(x+2)=0
	(x+2)(x+1)=0
	x=-2, x=-1
	"""

	x1 = -x1; x2 = -x2
	sign = lambda n: '+' if n >= 0 else ''
	print('x^2 %s %dx %s %d = 0' % (sign(x1+x2),x1+x2,sign(x1*x2), x1*x2))
	print('x^2 %s %dx %s %dx %s %d = 0' % (sign(x1),x1,sign(x2),x2,sign(x1*x2),x1*x2) )
	print('x(x %s %d) %s %d(x %s %d) = 0' % (sign(x1), x1, sign(x2), x2,sign(x1), x1))
	print('(x %s %d)(x %s %d) = 0' % (sign(x1), x1, sign(x2), x2))
	print('x = %d or x = %d' % (-x1,-x2))

