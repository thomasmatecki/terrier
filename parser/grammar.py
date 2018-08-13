from parser.combos import *
from itertools import zip_longest
from django.db.models import F, Q


class CommonExpr:
  __slots__ = ()

  def __init__(self, *args, **kwargs):
    for arg, slot in zip_longest(args, self.__slots__):
      setattr(self, slot, arg)


class PrimitiveLiteral(CommonExpr):
  __slots__ = 'value',

  @property
  def v(self):
    return self.value


class Identifier(CommonExpr):
  __slots__ = 'name',

  @property
  def v(self):
    return F(self.name)


class RelationExpr(CommonExpr):
  __slots__ = 'common_expr',

  _k = ''

  @property
  def k(self):
    return self.common_expr.name + self._k


class ComparisonExpr(CommonExpr):
  __slots__ = 'relation_expr', 'common_expr',

  @property
  def q(self):
    k = self.relation_expr.k
    v = self.common_expr.v

    return Q(**{k: v})


class BooleanCommonExpr(CommonExpr):
  __slots__ = 'bool_expr', 'conjunction_expr',


class ConjunctionExpr(CommonExpr):
  __slots__ = 'bool_common_expr',


class BooleanParenExpr(CommonExpr):
  __slots__ = 'bool_common_expr',


EqExpr = type('EqExpr', (RelationExpr,), {})
NeExpr = type('NeExpr', (RelationExpr,), {'_k': '__ne'})
LtExpr = type('LtExpr', (RelationExpr,), {'_k': '__lt'})
LeExpr = type('LeExpr', (RelationExpr,), {'_k': '__lte'})
GtExpr = type('GtExpr', (RelationExpr,), {'_k': '__gt'})
GeExpr = type('GeExpr', (RelationExpr,), {'_k': '__ge'})

AndExpr = type('AndExpr', (ConjunctionExpr,), {})
OrExpr = type('OrExpr', (ConjunctionExpr,), {})

# Grammar:

BWS = RE(r"\s*")
RWS = RE(r"\s+")
OPEN = RE(r"\(")
CLOSE = RE(r"\)")

integerLiteral = RE(r"(\d+)") >> int
stringLiteral = RE(r"'(\w+)'") >> str

primitiveLiteral = (integerLiteral | stringLiteral) >> PrimitiveLiteral
identifier = RE(r"(\w+)") >> Identifier

commonExpr = (primitiveLiteral | identifier)

eqExpr = commonExpr + (RWS + 'eq' + RWS) >> EqExpr
neExpr = commonExpr + (RWS + 'ne' + RWS) >> NeExpr
ltExpr = commonExpr + (RWS + 'lt' + RWS) >> LtExpr
leExpr = commonExpr + (RWS + 'le' + RWS) >> LeExpr
gtExpr = commonExpr + (RWS + 'gt' + RWS) >> GtExpr
geExpr = commonExpr + (RWS + 'ge' + RWS) >> GeExpr

relationExpr = (eqExpr | neExpr | ltExpr | leExpr | gtExpr | geExpr)
boolPredicateExpr = (relationExpr + commonExpr) >> ComparisonExpr

# By convention, how about forward declared expressions(i.e lazily evaluated,
# e.g. recursive parsers) are macro'ed with the same name and a preceding
# underscore?
_boolCommonExpr = L(lambda: boolCommonExpr)

andExpr = RWS + 'and' + RWS + _boolCommonExpr >> AndExpr
orExpr = RWS + 'or' + RWS + _boolCommonExpr >> OrExpr

conjunctionExpr = andExpr | orExpr

boolParenExpr = OPEN + BWS + _boolCommonExpr + BWS + CLOSE >> BooleanParenExpr

boolCommonExpr = ((boolPredicateExpr | boolParenExpr) * conjunctionExpr) >> BooleanCommonExpr
