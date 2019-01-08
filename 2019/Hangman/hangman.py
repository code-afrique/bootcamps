# Hangman Game
import random
import string

WORDLIST_FILENAME = "words.txt"


def load_words():
    """
    Returns a list of valid words. Words are strings of lowercase letters.

    Depending on the size of the word list, this function may
    take a while to finish.
    """
    print("Loading word list from file...")
    inFile = open(WORDLIST_FILENAME, 'r')
    line = inFile.readline()
    # wordlist: list of strings
    wordlist = line.split()
    print("  ", len(wordlist), "words loaded.")
    return wordlist


def choose_word(wordlist):
    """
    wordlist (list): list of words (strings)
    Returns a word from wordlist at random
    """
    return random.choice(wordlist)


# Load the list of words into the variable wordlist
# so that it can be accessed from anywhere in the program
wordlist = load_words()


def check_game_won(secret_word, letters_guessed):
    '''
    secret_word: string, the word the user is guessing; assumes all letters are
      lowercase
    letters_guessed: list (of letters), which letters have been guessed so far;
      assumes that all letters are lowercase
    returns: boolean, True if all the letters of secret_word are in letters_guessed;
      False otherwise
    '''
    if len(letters_guessed) == 0 :
        return False
    #else
    char_len = 0
    while(char_len != len(secret_word)): #if you have not counted total num of chars in word
        for char in secret_word:
            if letters_guessed.count(char)==1:
                char_len +=1
            else:
                return False
    return True
    
def get_word_progress(secret_word, letters_guessed):
    '''
    secret_word: string, the word the user is guessing; assumes the letters in
      secret_word are all lowercase.
    letters_guessed: list (of letters), which letters have been guessed so far
    returns: string, comprised of letters and carets (^) that represents
      which letters in secret_word have not been guessed so far.
        '''
    sec_word_len = len(secret_word)
    if len(letters_guessed) == 0:
        return (sec_word_len*"^")
    else:
        word=""
        for letter in secret_word:
            if letter in letters_guessed:
                word += letter
            else:
                word +="^"
        return word
        

def  get_remaining_possible_letters(letters_guessed):
    '''
    letters_guessed: list (of letters), which letters have been guessed so far
    returns: string (of letters), comprised of letters that represents which 
    letters have not yet been guessed. The letters should be returned in
    alphabetical order.
    '''
    import string
    if letters_guessed == 0:
        return string.ascii_lowercase
    else:
        all_letters = string.ascii_lowercase
        for letter in letters_guessed:
            if letter in all_letters:
                i = all_letters.index(letter)
                str_1 = all_letters[:i]
                str_2 = all_letters[i+1:]
                all_letters = str_1 + str_2
            else:
                return all_letters
        return all_letters
    

def calculated_score(i,letters_guessed,secret_word):
    '''
    This function takes in takes in the remaining number of guesses ,
    letters guessed and secret_word in order to calculate the player's
    score when he or she wins
    '''
    unique_letters = 0
    for letter in letters_guessed:
        if letter in secret_word:
            unique_letters += 1
        else:
            unique_letters = unique_letters
    return(2*i) + (3*unique_letters*len(secret_word))
    

def game_termination(letters_guessed,secret_word):
    '''
    This function checks to see whether the game should terminate or not.
    It checks to see whether the player has guessed the coerrect word or
    it checks if the number of guesses is zero.
    '''
    return check_game_won(secret_word, letters_guessed)

def valid_input(letter_guess):
    '''
    This function checks whether the input from the user is valid, 
    that is that it is a letter in the alphabet.
    '''
    for char in string.ascii_lowercase:
        if char==letter_guess:
            return True
    return False      

def hangman(secret_word):
    '''
    secret_word: string, the secret word to guess.

    Starts up an interactive game of Hangman.

    * At the start of the game, let the user know how many 
      letters the secret_word contains and how many guesses they start with.

    * The user should start with 10 guesses.

    * Before each round, you should display to the user how many guesses
      they have left and the letters that the user has not yet guessed.

    * Ask the user to supply one guess per round. Remember to make
      sure that the user puts in a letter!

    * The user should receive feedback immediately after each guess 
      about whether their guess appears in the computer's word.

    * After each guess, you should display to the user the 
      partially guessed word so far.

    Follows the other limitations detailed in the problem write-up.
    '''
    length_secret_word = len(secret_word)
    print("Welcome to Hangman!")
    print("I am thinking of a word that is", length_secret_word, "letters long")   
    print("---------------------")
    letters_guessed = []
    num_guesses = 10
    while num_guesses > 0 and game_termination(letters_guessed,secret_word)==False:
        print("You have", num_guesses, "guesses left")
        print("Available letters:", get_remaining_possible_letters(letters_guessed))
        letter_guess = input("Please guess a letter: ")
        if valid_input(letter_guess):
            if letters_guessed.count(letter_guess)==0:
                letters_guessed.append(letter_guess)
                if letter_guess in secret_word:
                    print("Good guess: ", get_word_progress(secret_word, letters_guessed))
                else:
                    print("Oops! That letter is not in my word:", get_word_progress(secret_word, letters_guessed))
                    num_guesses = num_guesses-1
            else:
                print("Oops! You've already guessed that letter:", get_word_progress(secret_word, letters_guessed))
        else:
            print("Oops! That is not a valid letter. Please input a letter from the alphabet:", get_word_progress(secret_word, letters_guessed))
        print("---------------------")  
    if num_guesses==0:
        print("Awww! You lost!", "The word was:", secret_word)
    else:
        print("Congratulations, you won! Your total score for this game is: ", calculated_score(num_guesses,letters_guessed,secret_word))
                                    

# When you've completed your hangman function, scroll down to the bottom
# of the file and uncomment the lines to test
# (hint: you might want to pick your own
# secret_word while you're doing your own testing)

def choose_from_these(secret_word, letters_guessed):
    choose_from_list= []
    remaining_letters = get_remaining_possible_letters(letters_guessed)
    for letter in remaining_letters:
        if letter in secret_word:
            choose_from_list.append(letter)
    s=""
    return s.join(choose_from_list)

# secret_word ="happy"
# hangman(secret_word)

# secret_word = "justice"
# hangman(secret_word)
#To add more levels to the game, create a new secret word variable and call the hangman function on it. 



                   


