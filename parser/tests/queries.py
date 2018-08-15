from parser.grammar import *


def test_eq_query():
  bc0 = boolCommonExpr <= 'Foo eq 5'

  q0 = bc0.Q
