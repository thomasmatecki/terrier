from parser.grammar import *
from functools import reduce


def _check(check_item, actual):
  key, expected = check_item

  path = key.split(".")

  for attr_name in path:
    actual = getattr(actual, attr_name)

  if isinstance(expected, type):
    return isinstance(actual, expected)
  else:
    return expected == actual


def expected(result, cls: type, attr: dict, idx=None):
  if idx is not None:
    result = result[idx]

  return reduce(lambda acc, item: acc and _check(item, result),
                attr.items(),
                isinstance(result, cls))


def test_primitiveLiteral():
  assert "Foo" == (stringLiteral <= "'Foo'")
  assert 5 == (integerLiteral <= "5")

  assert expected(primitiveLiteral <= "5", PrimitiveLiteral, {'value': 5})


def test_identifier():
  assert expected(identifier <= "Foo", Identifier, {'name': "Foo"})


def test_commonExpr():
  assert expected(commonExpr <= "'Foo'", CommonExpr, {'value': "Foo"}, 0)
  assert expected(commonExpr <= "5", CommonExpr, {'value': 5}, 0)
  assert expected(commonExpr <= "Foo", CommonExpr, {'name': "Foo"}, 0)


def test_relationExprs():
  assert expected(eqExpr <= '5 eq ', EqExpr, {'common_expr': PrimitiveLiteral,
                                              'common_expr.value': 5})


def test_comparisonExpr():
  assert expected(boolPredicateExpr <= 'Foo eq 5',
                  ComparisonExpr,
                  {'relation_expr': EqExpr,
                   'relation_expr.common_expr': Identifier,
                   'relation_expr.common_expr.name': 'Foo',
                   'common_expr': PrimitiveLiteral,
                   'common_expr.value': 5})

  assert expected(boolPredicateExpr <= "'Thomas' eq FirstName",
                  ComparisonExpr,
                  {'common_expr': Identifier,
                   'common_expr.name': "FirstName",
                   'relation_expr': EqExpr,
                   'relation_expr.common_expr': PrimitiveLiteral,
                   'relation_expr.common_expr.value': 'Thomas'})


def test_boolCommonExpr():
  bc0 = boolCommonExpr <= 'Foo eq 5'

  bc1 = boolCommonExpr <= 'Foo eq 5 and Bar le 5'

  bc3 = boolCommonExpr <= 'Foo eq 5 and (Bar le 5)'

  bc3 = boolCommonExpr <= "Foo eq 5 or (Bar le 5 and FirstName eq 'Thomas' )"

  bc4 = boolCommonExpr <= "Age gt 30 or (Age le 30 and FirstName eq 'Thomas' ) or LastName eq 'Matecki'"

  res = bc4.Q

