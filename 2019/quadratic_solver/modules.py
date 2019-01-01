###### DO NOT MODIFY ANYTHING IN THIS FILE ############
import math
import matplotlib.pyplot as graph

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


	# TODO: 
	# handle equations that do not have real roots, rational roots, etc 
	# draw graphs
	# better input method