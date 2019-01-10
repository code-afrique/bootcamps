###### DO NOT MODIFY ANYTHING IN THIS FILE ############
import math
from	unittest import TestCase as test
from fractions import gcd 
import matplotlib.pyplot as plot

def graph(x1,x2):
	a=[]
	b=[]
	# y=0
	# x=-50

	for x in range(x1 - 10, x2 - 10, 1):
			y=x**2+2*x+2
			a.append(x)
			b.append(y)

	fig= plot.figure()
	axes=fig.add_subplot(111)
	axes.plot(a,b)
	plot.show()


def print_step_by_step(a,b,c,x1,x2):
	d = b**2 - 4.0*a*c
	r1 = (-b - math.sqrt(d)) / (2.0*a)
	r2 = (-b + math.sqrt(d)) / (2.0*a)

	test.assertEqual(r2, x1)
	test.assertEqual(r2, x2)