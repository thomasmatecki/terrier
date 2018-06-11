from parser.combos import *


class CommonExpr:
  pass


class PrimitiveLiteral(CommonExpr):
  def __init__(self, value):
    self.value = value


class Identifier(CommonExpr):
  def __init__(self, name):
    self.name = name


class RelationExpr(object):
  def __init__(self, common_expr):
    self.common_expr = common_expr


EqExpr = type('EqExpr', (RelationExpr,), {})
NeExpr = type('NeExpr', (RelationExpr,), {})
LtExpr = type('LtExpr', (RelationExpr,), {})
LeExpr = type('LeExpr', (RelationExpr,), {})
GtExpr = type('GtExpr', (RelationExpr,), {})
GeExpr = type('GeExpr', (RelationExpr,), {})


class ComparisonExpr(object):
  def __init__(self, common_expr, relation_expr):
    self.common_expr = common_expr
    self.relation_expr = relation_expr


class BooleanCommonExpr(object):
  def __init__(self, bool_expr, conjunction_expr=None):
    self.bool_expr = bool_expr
    self.conjunction_expr = conjunction_expr


class BooleanParenExpr:
  def __init__(self, bool_common_expr):
    self.bool_common_expr = bool_common_expr


class ConjunctionExpr(object):
  def __init__(self, bool_common_expr):
    self.bool_common_expr = bool_common_expr


AndExpr = type('AndExpr', (ConjunctionExpr,), {})
OrExpr = type('OrExpr', (ConjunctionExpr,), {})

BWS = RE(r"\s*")
RWS = RE(r"\s+")
OPEN = RE(r"\(")
CLOSE = RE(r"\)")

integerLiteral = RE(r"(\d+)") >> int
stringLiteral = RE(r"'(\w+)'") >> str

primitiveLiteral = (integerLiteral | stringLiteral) >> PrimitiveLiteral
identifier = RE(r"(\w+)") >> Identifier

commonExpr = (primitiveLiteral | identifier)

eqExpr = RWS + 'eq' + RWS + commonExpr >> EqExpr
neExpr = RWS + 'ne' + RWS + commonExpr >> NeExpr
ltExpr = RWS + 'lt' + RWS + commonExpr >> LtExpr
leExpr = RWS + 'le' + RWS + commonExpr >> LeExpr
gtExpr = RWS + 'gt' + RWS + commonExpr >> GtExpr
geExpr = RWS + 'ge' + RWS + commonExpr >> GeExpr

relationExpr = (eqExpr | neExpr | ltExpr | leExpr | gtExpr | geExpr)
boolPredicateExpr = (commonExpr + relationExpr) >> ComparisonExpr

# By convention, how about forward declared expressions(i.e lazily evaluated,
# e.g. recursive parsers) are macro'ed with the same name and a preceding
# underscore?
_boolCommonExpr = L(lambda: boolCommonExpr)

andExpr = RWS + 'and' + RWS + _boolCommonExpr >> AndExpr
orExpr = RWS + 'or' + RWS + _boolCommonExpr >> OrExpr

conjunctionExpr = andExpr | orExpr

boolParenExpr = OPEN + BWS + _boolCommonExpr + BWS + CLOSE >> BooleanParenExpr

boolCommonExpr = ((boolPredicateExpr | boolParenExpr) * conjunctionExpr) >> BooleanCommonExpr
