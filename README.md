# terrier (Work In Progress)
### A Simple REST Query Protocol
Slowly attempting to implement a (partially compliant) [OData V4](http://docs.oasis-open.org/odata/odata/v4.01/odata-v4.01-part1-protocol.html) processor for Django endpoints (or something like that). 

The idea here is to parse the OData URI into a query against a [Django data model](https://docs.djangoproject.com/en/2.0/topics/db/) and avoid filtering and aggregating a (possibly large) set of records in the application layer (like the [Apache Olingo library](https://olingo.apache.org/doc/odata4/tutorials/sqo_f/tutorial_sqo_f.html)). Basically, this is just a URI parser and therefore includes a simple [parser combinator library](https://github.com/thomasmatecki/PyREST/blob/master/parser/combos.py) that is used to construct a parser from a syntax declared using a simple ABNF(/EBNF)-like format:

```
BWS = RE(r"\s*")
RWS = RE(r"\s+")
OPEN = RE(r"\(")
CLOSE = RE(r"\)")

integerLiteral = RE(r"(\d+)")
stringLiteral = RE(r"'(\w+)'")
primitiveLiteral = (integerLiteral | stringLiteral) 
identifier = RE(r"(\w+)")
commonExpr = (primitiveLiteral | identifier)

eqExpr = RWS + 'eq' + RWS + commonExpr 
neExpr = RWS + 'ne' + RWS + commonExpr 
ltExpr = RWS + 'lt' + RWS + commonExpr 
leExpr = RWS + 'le' + RWS + commonExpr 
gtExpr = RWS + 'gt' + RWS + commonExpr 
geExpr = RWS + 'ge' + RWS + commonExpr 

relationExpr = (eqExpr | neExpr | ltExpr | leExpr | gtExpr | geExpr)
boolPredicateExpr = (commonExpr + relationExpr) 
_boolCommonExpr = L(lambda: boolCommonExpr)

andExpr = RWS + 'and' + RWS + _boolCommonExpr 
orExpr = RWS + 'or' + RWS + _boolCommonExpr
conjunctionExpr = andExpr | orExpr
boolParenExpr = OPEN + BWS + _boolCommonExpr + BWS + CLOSE 
boolCommonExpr = ((boolPredicateExpr | boolParenExpr) * conjunctionExpr) 
```

The definition above ([also this](https://github.com/thomasmatecki/PyREST/blob/master/parser/grammar.py)) is a meager start to an implemenation of the complete [OData ABNF syntax](https://docs.oasis-open.org/odata/odata/v4.0/errata02/os/complete/abnf/odata-abnf-construction-rules.txt) 
