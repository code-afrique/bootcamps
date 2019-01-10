import introcs
from quadratic_solver import check_roots, solve

def test_discriminant():
  print("Testing check_roots function.")

  introcs.assert_equals('real roots',check_roots(1,3,2))
  introcs.assert_equals('equal roots',check_roots(1,2,1))
  introcs.assert_equals('complex roots',check_roots(5,1,1))

  print("check_roots function looks ok\n")


def test_solve():
  print("Testing solve function.")
  eval_1 = solve(1,3,2)
  introcs.assert_equals((-2, -1), (min(eval_1), max(eval_1)))

  eval_2 = solve(5,6,1)
  introcs.assert_equals((-1, -0.2), (min(eval_2), max(eval_2)))
  print("solve function looks ok\n")


if __name__ == '__main__':
  test_discriminant()
  test_solve()
  print("Yay! - All tests passed successfully")

