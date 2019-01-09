###### DO NOT MODIFY ANYTHING IN THIS FILE ############
import math
from	unittest import TestCase as test
from fractions import gcd 
import matplotlib.pyplot as graph


def print_step_by_step(a,b,c,x1,x2):
	d = b**2 - 4.0*a*c
	r1 = (-b - math.sqrt(d)) / (2.0*a)
	r2 = (-b + math.sqrt(d)) / (2.0*a)

	test.assertEqual(r2, x1)
	test.assertEqual(r2, x2)