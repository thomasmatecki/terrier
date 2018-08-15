from parser.combos import *
from itertools import zip_longest
from django.db.models import F, Q


class InvalidQueryException(Exception):
  pass


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

  @property
  def k(self):
    raise InvalidQueryException()


class Identifier(CommonExpr):
  __slots__ = 'name',

  @property
  def v(self):
    return F(self.name)

  k = v


class RelationExpr(CommonExpr):
  __slots__ = 'common_expr',

  _k = ''

  @property
  def k(self):
    return self.common_expr.name + self._k

  def _opposite(self):
    return self

  @property
  def opposite(self):
    return self._opposite()


class ComparisonExpr(CommonExpr):
  __slots__ = 'relation_expr', 'common_expr',

  @property
  def _transpose(self):
    return ComparisonExpr(self.relation_expr.opposite(self.common_expr),
                          self.relation_expr.common_expr)

  @property
  def Q(self) -> Q:
    """
    The result is a Q object that takes a dictionary with keys that are fields in the
    assignment position of **kwargs; i.e:

      color eq 'yellow' -> {'color' : 'yellow'} -> color=yellow
      
    If the Comparison expression has a field in both, positions, that's fine. Use the 
    'name' in key (the assignment target) and the F object in the target:
    
      color eq flavor -> {'color' : F('flavor')} -> color=F('flavor')

    If there is a primitive literal in the assignment position, then transpose. If this is
    still true, let the `k` method of primitive literal throw an error. e.g.:

      'yellow' eq 'red' -> 'red' eq 'yellow' -> No Dice...

    :return: django.db.models.Q object
    """
    if isinstance(self.relation_expr.common_expr, PrimitiveLiteral):
      return self._transpose.Q
    else:
      return Q(**{self.relation_expr.k: self.common_expr.v})


def identity(x):
  return x


class BooleanCommonExpr(CommonExpr):
  __slots__ = 'bool_expr', 'conjunction_expr',

  @property
  def Q(self):
    # if self.conjunction_expr:
    #   return self.conjunction_expr.C(self.bool_expr.Q)
    # else:
    return self.bool_expr.Q


class ConjunctionExpr(CommonExpr):
  __slots__ = 'bool_common_expr',


class BooleanParenExpr(CommonExpr):
  __slots__ = 'bool_common_expr',


EqExpr = type('EqExpr', (RelationExpr,), {})
NeExpr = type('NeExpr', (RelationExpr,), {'_k': '__ne'})
LtExpr = type('LtExpr', (RelationExpr,), {'_k': '__lt', '_opposite': lambda: GtExpr})
LeExpr = type('LeExpr', (RelationExpr,), {'_k': '__lte', '_opposite': lambda: GeExpr})
GtExpr = type('GtExpr', (RelationExpr,), {'_k': '__gt', '_opposite': lambda: LtExpr})
GeExpr = type('GeExpr', (RelationExpr,), {'_k': '__gte', '_opposite': lambda: LeExpr})

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
