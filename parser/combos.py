import re
from typing import Any, Union


class Extractor(object):

  def extract(self, expr: object) -> tuple:
    """
    Returns a tuple containing:
         [0] : A tuple of values extracted from `expr`.
         [1] : the remaining portion of `expr` not matched by the extractor.
    """
    raise NotImplementedError()

  # @property
  # def _cls(self):
  #   return self.__class__

  def __add__(self, other):
    return Then(self, other)

  def __or__(self, other):
    return Either(self, other)

  def __rshift__(self, call):
    return Match(self, call)


class Builder(Extractor):
  """

  """

  @classmethod
  def parse(cls, builder, expression, exact=True):
    """

    :param builder:
    :param expression:
    :param exact: Return an `None` if the complete `expression`
                  is not parsed(i.e. build returns a tail).
    :return:
    """
    built = builder.build(expression)

    if exact and built[1]:
      return None  # ... or maybe throw?

    return built[0]

  def build(self, expr):
    raise NotImplementedError()

  def extract(self, expr: Any) -> Union[tuple, None]:
    parsed = self.build(expr)

    if not parsed:
      return
    elif isinstance(parsed[0], tuple):
      return parsed
    else:
      return (parsed[0],), parsed[1]

  def __mul__(self, other):
    return Then(self, Maybe(other))

  def __pow__(self, other, modulo=None):
    return Then(self, Many(Maybe(other)), )

  def __lshift__(self, expression):
    return Builder.parse(self, expression, exact=False)

  def __le__(self, expression):
    return Builder.parse(self, expression)

  def __pos__(self):
    return Many(self)


class Match(Builder):
  """

  """

  def __init__(self, extractor, call=tuple):
    self._extractor = extractor
    self._call = call

  def build(self, expr):
    extracted = self._extractor.extract(expr)

    if extracted:
      args, tail = extracted
      return self._call(*args), tail


class Either(Builder):
  """

  """

  def __init__(self, left: Extractor, right: Extractor):
    self._left = left
    self._right = right

  def build(self, expr):
    parsed = self._left.extract(expr)
    if parsed:
      return parsed
    else:
      return self._right.extract(expr)


class Then(Builder):
  """

  """

  def __init__(self, first, then: Builder):
    self._first = first
    self._then = then

  def build(self, expr):
    extracted = self._first.extract(expr)
    if extracted:
      args, tail = extracted

      next_extracted = self._then.extract(tail)
      if next_extracted:
        next_args, tail = next_extracted

        args = args + next_args
        return args, tail


class Maybe(Builder):
  """

  """

  def __init__(self, extractor):
    self.extr = extractor

  def build(self, expr):
    extracted = self.extr.extract(expr)
    if extracted:
      args, tail = extracted
      return args, tail
    else:
      return (), expr


class Many(Builder):

  def __init__(self, extractor: Builder):
    self.extr = extractor

  def build(self, expr):
    """
    Extract recursively WHILE extraction is successful AND the tail is consumed.

    Use with a `Maybe` builder to extract 0..N repeated expressions. Without a `Maybe`
    builder, extracts 1..N repeated expressions. `call` is not applied for each
    recursion, and therefore should accept a variable number of arguments.
    :param expr:
    :return:
    """
    extracted = self.extr.extract(expr)

    if not extracted:
      return None

    args, tail = extracted

    if tail != expr:
      next_extracted = self.extract(tail)

      if next_extracted:
        next_args, tail = next_extracted
        args = args + next_args

    return args, tail


class Lazy(Builder):
  """

      .. code-block::
      Foo(*args0..., Foo(*args1..., Foo(...))) ).

  """

  def __init__(self, extr_call):
    assert callable(extr_call)
    self._extr_call = extr_call

  def build(self, expr):
    extractor = self._extr_call()

    extracted = extractor.extract(expr)

    if extracted:
      args, tail = extracted
      return args, tail


class RegExpr(Extractor):
  """

  """

  def __init__(self, pattern):
    self.pattern = pattern

  def extract(self, expr):
    match = re.match(self.pattern, expr)
    if match:
      fr, to = match.span()
      return match.groups(), expr[to:]

  def __add__(self, other):
    if isinstance(other, str):
      return RegExpr(self.pattern + other)
    elif isinstance(other, RegExpr):
      return RegExpr(self.pattern + other.pattern)
    else:
      return Match(self) + other

  def __radd__(self, other):
    return other + self


# Abbreviations
L = Lazy
RE = RegExpr
