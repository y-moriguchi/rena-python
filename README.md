# Rena Python
Rena Python is a library of parsing texts. Rena Python makes parsing text easily.  
Rena Python can treat recursion of pattern, hence Rena Python can parse languages which described top down parsing
like arithmetic expressions and so on.  
Rena Python can parse class of Parsing Expression Grammar (PEG) language.  
Rena Python can also treat synthesized and inherited attributes.  
'Rena' is an acronym of REpetation (or REcursion) Notation API.  

## How to use

Use module:
```python
from rena import *
```

## Expression

### Construct Expression Generation Object
```python
r = rena.Rena(option)
```

Options shown as follows are available.
```
{
  "ignore": expression to ignore,
  "keys": [key, ...]
}
```

An example which generates object show as follows.
```python
s = rena.Rena()
r = rena.Rena({ "ignore": s.re("\s+"), "keys": ["+", "-", "++"] })
```

### Matching Expression
To apply string to match to an expression, call the expression with 3 arguments shown as follows.
1. a string to match
2. an index to begin to match
3. an initial attribute

return value of the expression is a tuple which has 3 elements
1. matched string or None if it is not matched
2. last index of matched string or None if it is not matched
3. result attribute or None if it is not matched

```python
match = r.oneOrMore(r.re("[0-9]"), lambda match, synthesized, inherited: inherited + ":" + match)
match("27", 0, "")   # outputs ('27', 2, ':2:7')
match("aa", 0, "")   # outputs (None, None, None)
```

### Elements of Expression

#### Literals
String literal of Python are elements of expression.  
To use only one literal as expression, use then synthesized expression.

#### Regular Expression
Regular expression is an element of expression.
```python
r.re(regular expression)
```

#### Attrinbute Setting Expression
Attribute setting expression is an element of expression.
```python
r.attr(attribute to set)
```

#### Key Matching Expression
Key matching expression is an element of expression.  
If keys "+", "++", "-" are specified by option, below expression matches "+" but does not match "+" after "+".
```
r.key("+")
```

#### Not Key Matching Expression
Not key matching expression is an element of expression.
If keys "+", "++", "-" are specified by option, "+", "++", "-" will not match.
```
r.notKey()
```

#### Keyword Matching Expression
Keyword matching expression is an element of expression.
```
r.equalsId(keyword)
```

The table shows how to match expression r.equalsId("keyword") by option.

|option|keyword|keyword1|keyword-1|keyword+|
|:-----|:------|:-------|:--------|:-------|
|no options|match|match|match|match|
|ignore: "-"|match|no match|match|no match|
|keys: ["+"]|match|no match|no match|match|
|ignore: "-" and keys: ["+"]|match|no match|match|match|

#### Real Number
Real number expression is an element of expression and matches any real number.
```
r.real()
```

#### Newline
Newline expression is an element of expression and matches CR/LF/CRLF newline.
```
r.br()
```

#### End of string
End of string is an element of expression and matches the end of string.
```
r.end()
```

#### Function
Function which fulfilled condition shown as follow is an element of expression.  
* the function has 3 arguments
* first argument is a string to match
* second argument is last index of last match
* third argument is an attribute
* return value of the function is a tuple which has 3 elements
  1. matched string or None if it is not matched
  2. last index of matched string or None if it is not matched
  3. result attribute or None if it is not matched

Every instance of expression is a function fulfilled above condition.

### Synthesized Expression

#### Sequence
Sequence expression matches if all specified expression are matched sequentially.  
Below expression matches "abc".
```
r.then("a", "b", "c")
```

#### Choice
Choice expression matches if one of specified expression are matched.  
Specified expression will be tried sequentially.  
Below expression matches "a", "b" or "c".
```
r.choice("a", "b", "c")
```

#### Repetation
Repetation expression matches repetation of specified expression.  
The family of repetation expression are shown as follows.  
```
r.times(minimum count, maximum count, expression, [action])
r.atLeast(minimum count, expression, [action])
r.atMost(maximum count, expression, [action])
r.oneOrMore(expression, [action])
r.zeroOrMore(expression, [action])
r.maybe(expression)
```

r.atLeast(min, expression, action) is equivalent to r.times(min, false, expression, action).  
r.atMost(max, expression, action) is equivalent to r.times(0, max, expression, action).  
r.oneOrMore(expression, action) is equivalent to r.times(1, false, expression, action).  
r.zeroOrMore(expression, action) is equivalent to r.times(0, false, expression, action).  
r.maybe(expression) is equivalent to r.times(0, 1, expression).  

The argument action must specify a function with 3 arguments and return result attribute.  
First argument of the function will pass a matched string,
second argument will pass an attribute of repetation expression ("synthesized attribtue"),
and third argument will pass an inherited attribute.  

For example, consider action of the expression.
```python
match = r.oneOrMore(r.re("[0-9]"), lambda match, synthesized, inherited: inherited + ":" + match)
match("27", 0, "")
```

In first match of string "27", the arguments of function are ("2", "", "") and results ":2".  
In second match, the arguments are ("7", "", ":2") and results ":2:7".

Repetation expression is already greedy and does not backtrack.

#### Repetation with Delimiter
Repetation with delimiter matches repetation one or more times and delimited by delimiter expression.  
Below expression matches "1,2,3".
```python
r.delimit(r.re("[0-9]+"), ",")
```

The r.delimit can pass an action as third arguments same as simple repetation.

#### Lookahead (AND predicate)
Lookahead (AND predicate) matches the specify expression but does not consume input string.
Below example matches "ab" but matched string is "a", and does not match "ad".
```python
r.then("a", r.lookahead("b"))
```

#### Nogative Lookahead (NOT predicate)
Negative lookahead (NOT predicate) matches if the specify expression does not match.
Below example matches "ab" but matched string is "a", and does not match "ad".
```python
r.then("a", r.lookaheadNot("d"))
```

#### Condition
Condition expression matches if the predicate function returns true.  
Below example matches if the attribute is "765", but does not match if the attribute is "961".
```python
r.cond(lambda attr: attr == "765")
```

#### Action
Action expression matches the specified expression.  
```python
r.action(expression, action)
```

The second argument must be a function with 3 arguments and return result attribute.  
First argument of the function will pass a matched string,
second argument will pass an attribute of repetation expression ("synthesized attribtue"),
and third argument will pass an inherited attribute.  

Below example, argument of action will be passed ("2", "2", "").
```python
r.action(r.re("[0-9]"), lambda match, synthesized, inherited: match)("2", 0, "")
```

### Description of Recursion
The r.letrec function is available to recurse an expression.  
The argument of r.letrec function are functions, and return value is the return value of first function.

Below example matches balanced parenthesis.
```python
def parenFunction(paren):
  return r.then("(", r.maybe(paren), ")")

paren = r.letrec(parenFunction)
paren("((()))", 0, 0)  # output ('((()))', 6, 0)
paren("((())", 0, 0)   # output (None, None, None)
```

## Examples

### Parsing simple arithmetic expressions
```python
r = rena.Rena()
def term(term, factor, element):
  return r.then(factor,
           r.zeroOrMore(r.choice(
             r.action(r.then("+", factor), lambda match, synthesized, inherit: inherit + synthesized),
             r.action(r.then("-", factor), lambda match, synthesized, inherit: inherit - synthesized))))

def factor(term, factor, element):
  return r.then(element,
           r.zeroOrMore(r.choice(
             r.action(r.then("*", element), lambda match, synthesized, inherit: inherit * synthesized),
             r.action(r.then("/", element), lambda match, synthesized, inherit: inherit / synthesized))))

def element(term, factor, element):
  return r.choice(r.real(), r.then("(", term, ")"))

expr = r.letrec(term, factor, element)

expr("1+2*3", 0, 0)[2]    # outputs 7
expr("4-6/2", 0, 0)[2]    # outputs 1
expr("(4-6)/2", 0, 0)[2]  # outputs -1
```

### Parsing CSV texts
```python
r = rena.Rena()
csvparser = r.then(r.attr([]),
  r.maybe(r.delimit(
    r.action(r.then(
      r.attr([]),
      r.delimit(r.choice(
        r.then(
          '"',
          r.action(r.re('(""|[^"])+'), lambda match, synthesize, inherit: inherit + [match.replace('""', '"')]),
          '"'),
        r.action(r.re('[^",\n\r]+'), lambda match, synthesize, inherit: inherit + [match])
      ), ',')), lambda match, synthesize, inherit: inherit + [synthesize]), r.br())),
  r.maybe(r.br()),
  r.end())

# outputs [["a","b","c"],["d","e\n\"f","g"],["h"]]
csvparser('a,b,c\nd,"e\n""f",g\nh\n', 0, 0)[2]
```

