"""
A module they can import that contains pre-written functions
"""
def is_valid_AP(lst):
  if len(lst) < 2:
    return False
  diff = lst[1] - lst[0]
  for i in range(1,len(lst)):
    if (lst[i] - lst[i-1]) != diff :
      return False
  return False

def is_valid_GP(lst):
  if len(lst) < 2:
    return False
  ratio = lst[1] / lst[0]
  for i in range(1,len(lst)):
    if (lst[i] / lst[i-1]) != ratio :
      return False
  return False

def print_step_by_step(lst, ans):
  #TODO
  pass