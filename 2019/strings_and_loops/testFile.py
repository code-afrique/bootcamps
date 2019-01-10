from code_Afrique_soln_Sena import *
from words import words1, words2
import introcs

def checkCountString():

	introcs.assert_equals(11, countString(words1, "foreign"))
	introcs.assert_equals(9, countString(words1, "challenge"))
	introcs.assert_equals(0, countString(words2, "happy"))
	introcs.assert_equals(1, countString(words2, "individual"))


	print("countString Function succeeded")

checkCountString()


def checkReverseString():

	introcs.assert_equals("", reverseString(""))
	introcs.assert_equals("nac", reverseString("can"))
	introcs.assert_equals("yppah", reverseString("happy"))
	introcs.assert_equals("laudividni", reverseString("individual"))


	print("reverseString Function succeeded")


checkReverseString()
