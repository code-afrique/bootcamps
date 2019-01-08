import unittest
from hangman import * 

HIDDEN = "^" 

def compare_results(expected, actual):
    '''
    Used for comparing equality of answers with expected answers
    '''
    def almost_equal(x,y):
        if x == y or x.replace(' ', '') == y.replace(' ',''):
            return True
        return False

    exp = expected.strip()
    act = actual.strip()
    return almost_equal(exp, act)

class TestSuite(unittest.TestCase):
    def test_check_game_won(self):
            self.assertTrue(check_game_won('face', ['f','c','a','e']))
            self.assertFalse(check_game_won('moves', ['o','c','a','v','e']))

    def test_check_game_won_repeated_letters(self):
            self.assertTrue(check_game_won('bass', ['a','s','b','e']),
                "Failed with repeated letters")
            self.assertFalse(check_game_won('rare', ['f','t','r','e']),
                "Failed with repeated letters")

    def test_check_game_won_empty_string(self):
            self.assertTrue(check_game_won('', ['f','c','y','e']), 
                "Failed with the empty string")

    def test_check_game_won_empty_list(self):
            self.assertFalse(check_game_won('code', []),
                "Failed with the empty list")

    def test_get_word_progress(self):
            self.assertTrue(compare_results(get_word_progress('face', ['f','c','a','e']), 'face'))
            self.assertTrue(compare_results(get_word_progress('moves', ['o','c','a','v','e']), HIDDEN+'ove'+HIDDEN))

    def test_get_word_progress_repeated_letters(self):
            self.assertTrue(compare_results(get_word_progress('bass', ['a','s','b','e']), 'bass'),
                "Failed with repeated letters")
            self.assertTrue(compare_results(get_word_progress('rare', ['f','t','r','e']), 'r'+HIDDEN+'re'),
                "Failed with repeated letters")

    def test_get_word_progress_empty_string(self):
            self.assertTrue(compare_results(get_word_progress('', ['f','c','y','e']), ''),
                "Failed with the empty string")

    def test_get_word_progress_empty_list(self):
            self.assertTrue(compare_results(get_word_progress('code', []), HIDDEN*4),
                "Failed with the empty list")

    def test_get_remaining_possible_letters(self):
            self.assertEqual(get_remaining_possible_letters(['a','b','c','d']), 'efghijklmnopqrstuvwxyz')
            self.assertEqual(get_remaining_possible_letters(['z','p','x','b', 'b']), 'acdefghijklmnoqrstuvwy')
            self.assertEqual(get_remaining_possible_letters(['a','u','i','o','w']), 'bcdefghjklmnpqrstvxyz')

    def test_get_remaining_possible_letters_empty_string(self):
            self.assertEqual(get_remaining_possible_letters(list(string.ascii_lowercase)), '',
                "Failed to return the empty string")

    def test_get_remaining_possible_letters_empty_list(self):
            self.assertEqual(get_remaining_possible_letters([]), 'abcdefghijklmnopqrstuvwxyz',
                "Failed with the empty list")


if __name__ == '__main__':
    unittest.main()

