import unittest
from terrier.combos import *


class PrimitiveLiteral:
  def __init__(self, value):
    self.value = value


class Identifier:
  def __init__(self, name):
    self.name = name


class Comparison:
  def __init__(self, operand):
    self.operand = operand


class GT(Comparison):
  pass


class LT(Comparison):
  pass


class GE(Comparison):
  pass


class LE(Comparison):
  pass


class EQ(Comparison):
  pass


class BooleanExpr:
  def __init__(self, operand, comparison):
    self.operand = operand
    self.comparison = comparison


class AndExpr:
  def __init__(self, operand):
    self.operand = operand


class ComparisonExprS:
  def __init__(self, compExpr, *andExprs, ):
    self.comparison = compExpr
    self.andExprs = andExprs


class TestExtractors(unittest.TestCase):
  primitiveLiteral = RegExpr(r"'(\w+)'") >> PrimitiveLiteral
  identifier = RegExpr(r"(\w+)") >> Identifier
  commonExpr = primitiveLiteral | identifier
  RWS = RegExpr(r"\s+")
  BWS = RegExpr(r"\s*")

  eqExpr = RWS + 'eq' + RWS + commonExpr >> EQ
  ltExpr = RWS + 'lt' + RWS + commonExpr >> LT
  gtExpr = RWS + 'gt' + RWS + commonExpr >> GT
  leExpr = RWS + 'le' + RWS + commonExpr >> LE
  geExpr = RWS + 'ge' + RWS + commonExpr >> GE

  compExpr = commonExpr + (eqExpr | ltExpr | gtExpr | leExpr | geExpr) >> BooleanExpr
  andExpr = RWS + 'and' + RWS + compExpr >> AndExpr

  OPEN = BWS + RegExpr(r"\(") + BWS
  CLOSE = BWS + RegExpr(r"\)") + BWS

  def test_build_regexpr_matcher(self):
    primitiveLiteral = RegExpr(r"'(\w+)'") >> PrimitiveLiteral

    pl0 = primitiveLiteral.build("'Foo'")[0]
    assert pl0.value == "Foo"

    id0 = self.identifier.build("Bar")[0]
    assert id0.name == "Bar"

  def test_add_combinator(self):
    pass

  def test_or_builder(self):
    assert isinstance(self.commonExpr, Either)

    ce0, tail = self.commonExpr.build("'Foo'")
    assert isinstance(ce0[0], PrimitiveLiteral)

    ce1, tail = self.commonExpr.build("Bar")
    assert isinstance(ce1[0], Identifier)

  def test_arrow_notation(self):
    RWS = self.RWS

    # Verify left arrow notation:
    res = self.commonExpr <= "Bar"
    assert isinstance(*res, Identifier)

    eqOp = RWS + 'eq' + RWS
    assert isinstance(eqOp, RegExpr)
    assert eqOp.pattern == RWS.pattern + 'eq' + RWS.pattern
    assert isinstance(RWS + 'eq' + RWS + self.commonExpr, Then)

  def test_builder_combinators(self):
    eq0 = self.eqExpr.build(" eq 'Foo'")[0]
    assert isinstance(eq0, EQ)
    assert eq0.operand.value == 'Foo'

  def test_parse_combinator_expression(self):
    b0 = self.compExpr <= "Foo eq 'Bar'"
    assert isinstance(b0, BooleanExpr)
    assert isinstance(b0.operand, Identifier)
    assert b0.operand.name == "Foo"
    assert isinstance(b0.comparison, EQ)
    assert isinstance(b0.comparison.operand, PrimitiveLiteral)
    assert b0.comparison.operand.value == 'Bar'

    b1 = self.compExpr <= "'bar' gt foo"
    assert isinstance(b1, BooleanExpr)
    assert isinstance(b1.operand, PrimitiveLiteral)
    assert b1.operand.value == "bar"
    assert isinstance(b1.comparison, GT)
    assert isinstance(b1.comparison.operand, Identifier)
    assert b1.comparison.operand.name == 'foo'

    b2 = self.compExpr.extract("foobar")
    assert not b2

    assert isinstance(self.andExpr, Match)

    b3 = self.andExpr <= " and Foo eq 'Bar'"
    assert isinstance(b3, AndExpr)
    assert isinstance(b3.operand, BooleanExpr)
    o0 = b3.operand

    assert isinstance(o0, BooleanExpr)
    assert isinstance(o0.operand, Identifier)
    assert o0.operand.name == "Foo"
    assert isinstance(o0.comparison, EQ)
    assert isinstance(o0.comparison.operand, PrimitiveLiteral)
    assert o0.comparison.operand.value == 'Bar'

  def test_maybe_combinator(self):
    compoundComp = self.compExpr * self.andExpr >> ComparisonExprS

    cc0 = compoundComp <= "Lorem ge 'Ipsum' and Foo eq 'Bar'"
    assert cc0

    cc1 = compoundComp <= "Lorem ge 'Ipsum'"
    assert cc1

    # cc2[1] should contain unmatched expression
    cc2 = compoundComp << "Lorem ge 'Ipsum' and Foo eq 'Bar' and 'frankincense' le Mir"
    assert cc2

  def test_many_combinator(self):
    repeatComp = self.compExpr ** self.andExpr >> ComparisonExprS

    rc0 = repeatComp <= "Lorem ge 'Ipsum' and Foo eq 'Bar' and 'frankincense' le Mir"
    assert isinstance(rc0, ComparisonExprS)

    assert isinstance(rc0.comparison, BooleanExpr)
    assert isinstance(rc0.andExprs, tuple)

    assert isinstance(rc0.andExprs[0], AndExpr)
    assert isinstance(rc0.andExprs[1], AndExpr)

    rc1 = repeatComp <= "Lorem ge 'Ipsum'"
    assert isinstance(rc1, ComparisonExprS)

    assert isinstance(rc1.comparison, BooleanExpr)

  def test_lazy_builder(self):
    # A digit followed by EITHER a comman and another digit, or a period.
    recursiveExpr = RE(r"\s*(\d+)\s*") + (RE(r",") + L(lambda: recursiveExpr) | RegExpr(r"."))
    csl0 = recursiveExpr <= "1,2,3, 4,5 ,6."

    assert csl0 == ('1', '2', '3', '4', '5', '6')

    class LinkedList:
      head = None

      def __iter__(self):
        self.head = self
        return self

      def __next__(self):
        if not self.head:
          raise StopIteration

        res = self.head.element
        self.head = self.head.next

        return res

    class IntegerNode(LinkedList):
      def __init__(self, element, next: LinkedList = None):
        self.element = element
        if next:
          self.next = next
        else:
          self.next = None

    intListExpr = (RE(r"\s*(\d+)\s*") >> int) + (RE(r",") + L(lambda: intListExpr) | RegExpr(r".")) >> IntegerNode
    assert isinstance(intListExpr._call, type)
    assert isinstance(intListExpr._extractor, Then)
    assert isinstance(intListExpr._extractor._first, Match)
    assert isinstance(intListExpr._extractor._first._extractor, RegExpr)

    assert isinstance(intListExpr._extractor._then, Either)
    assert isinstance(intListExpr._extractor._then._left, Then)
    assert isinstance(intListExpr._extractor._then._left._first, Match)
    assert isinstance(intListExpr._extractor._then._left._first._extractor, RegExpr)
    assert isinstance(intListExpr._extractor._then._left._then, Lazy)
    assert isinstance(intListExpr._extractor._then._right, RegExpr)

    lil0 = intListExpr <= "1,2,3, 4,5 ,6."

    assert isinstance(lil0, IntegerNode)

    assert [i for i in lil0] == [1, 2, 3, 4, 5, 6]

  def test_paren_expression(self):
    word = RE("\s*(\w+)\s*")
    parenExpr = (self.OPEN + +L(lambda: parenExpr) + self.CLOSE) | word

    pe0 = parenExpr <= "((( Do) (Ra) ) (Me) Fo)"

    assert pe0 == ('Do', 'Ra', 'Me', 'Fo')


if __name__ == '__main__':
  unittest.main()
