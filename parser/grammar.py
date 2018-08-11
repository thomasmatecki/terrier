from parser.combos import *
from itertools import zip_longest


class CommonExpr:
  __slots__ = ()

  def __init__(self, *args, **kwargs):
    for arg, slot in zip_longest(args, self.__slots__):
      setattr(self, slot, arg)


class PrimitiveLiteral(CommonExpr):
  __slots__ = 'value',


class Identifier(CommonExpr):
  __slots__ = 'name',


class RelationExpr(CommonExpr):
  __slots__ = 'common_expr',


class ComparisonExpr(CommonExpr):
  __slots__ = 'common_expr', 'relation_expr',


class BooleanCommonExpr(CommonExpr):
  __slots__ = 'bool_expr', 'conjunction_expr',


class ConjunctionExpr(CommonExpr):
  __slots__ = 'bool_common_expr',


class BooleanParenExpr(CommonExpr):
  __slots__ = 'bool_common_expr',


EqExpr = type('EqExpr', (RelationExpr,), {})
NeExpr = type('NeExpr', (RelationExpr,), {})
LtExpr = type('LtExpr', (RelationExpr,), {})
LeExpr = type('LeExpr', (RelationExpr,), {})
GtExpr = type('GtExpr', (RelationExpr,), {})
GeExpr = type('GeExpr', (RelationExpr,), {})

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
