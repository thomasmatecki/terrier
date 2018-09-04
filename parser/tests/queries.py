from parser.grammar import *


def test_eq_query():
  bc0 = boolCommonExpr <= 'Foo eq 5'

  q0 = bc0.Q

  assert q0.children == [('Foo', 5)]

  bc1 = boolCommonExpr <= '5 eq Foo'

  q1 = bc1.Q

  bc2 = boolCommonExpr <= '5 eq 5'

  q2 = bc2.Q

  pass
