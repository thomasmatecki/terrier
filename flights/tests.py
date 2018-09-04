from django.test import TestCase

# Create your tests here.
from parser.grammar import boolCommonExpr


def test_and_expr_yield_and_query():
  filter_clause = "airline eq 'AA' and departure_airport eq 'JNU'"

  filter_ast = boolCommonExpr <= filter_clause

