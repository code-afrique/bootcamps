from words import *

##
### Fill in the functions below



#1
##This function takes both a list of elements and a string as 
#input and counts the number of times the string occurs in the list.

#Task:
#Using a for loop, please fill in the function body.

def countString(listOfWords, word):

	accumulator = 0

	for item in listOfWords:
		if word == item:
			accumulator += 1


	return accumulator


def reverseString(word):

	#Task:
	#Given a string, return the reversed version
	
	#Eg:
	#Given the word "Afrique," return "euqirfA"

	reversedWord = ""

	for letter in word:

		reversedWord = letter + reversedWord 

	return reversedWord


def main():

	allWords = words2

	print(countString(allWords, "individual"))

	print(reverseString("individual"))





if __name__ == '__main__':
	main()

