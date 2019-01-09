import random
import string

# Guess the Movie Game

# This game simply allows you to guess a movie randomly picked
# from a list that have been compiled. You guess one character at a time
# to fill in spaces provided hinting the number of characters in the movie
# You only have 10 trails to win this game
# Enjoy and I hope you have fun


#This function loads the movie list into our python program
def movie_logic():
    """
    the syntax below allows you to import the movie
    txt file into our python program.

    """
    #opens the movie file
    file = open("movies.txt", "r")

    #create an array and save the text file in an array
    movie_array = []

    #this loop was created to repeat the action within the loop till
    #the loop satisfies its condition. Notice the use of range(start, end, step)
    for i in range(0, 25, 1):
        #reads the movie list
        movies_file = file.readline()
        movie_list = movies_file.split()

        #adds the list to the movie_list_array
        movie_array.append(movie_list)
    return movie_array


MOVIE_STYLE = movie_logic()
print(MOVIE_STYLE)


def random_movie(movie_style):
    """
    This function select a random movie from the list of
    movies and then returns it
    """
    random_movie = random.choice(movie_style)
    print(random_movie)

    return random_movie

random_movie(MOVIE_STYLE)
