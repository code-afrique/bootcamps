import introcs
from quadratic_solver import check_roots, solve

def test_discriminant():
  tests_values = [
    ((1,3,2), 'real roots'),
    ((1,2,1), 'equal roots'),
    ((5,1,0), 'complex roots')
  ]

  for test in tests_values:
    args, expected_result = test
    introcs.assert_equals(expected_result,check_roots(test[0][1], test[0][1], test[0][2]))

  print("check_roots function passed successfully")


def test_solver():
  pass 


if __name__ == '__main__':
  test_discriminant()
  test_solver()

