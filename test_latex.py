import sympy
from sympy import latex as sympy_latex, symbols, Mul
x = symbols('x')

def latex(expr, **kwargs):
    if 'mul_symbol' not in kwargs:
        kwargs['mul_symbol'] = 'times'
    return sympy_latex(expr, **kwargs)

print(f"Symbolic 2*x: {latex(2*x)}")
print(f"Numeric 2*3: {latex(Mul(2, 3, evaluate=False))}")
