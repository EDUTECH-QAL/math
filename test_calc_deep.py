import sympy
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
import re

def sanitize_expression(expr_str):
    if not expr_str:
        return ""
    expr_str = expr_str.replace('^', '**')
    expr_str = expr_str.replace('÷', '/')
    expr_str = expr_str.replace('×', '*')
    expr_str = expr_str.replace('≤', '<=')
    expr_str = expr_str.replace('≥', '>=')
    if '|' in expr_str:
        expr_str = re.sub(r'\|([^|]+)\|', r'Abs(\1)', expr_str)
    return expr_str

def test_multiplication():
    transformations = (standard_transformations + (implicit_multiplication_application,))
    
    expressions = [
        "2*3",
        "2(3)",
        "2x",
        "2 3",
        "2.5 * 4",
        "2,5 * 4", # Common in some regions
        "2*3+4",
        "2*(3+4)",
        "5x",
        "5 x", # This might be the issue
    ]
    
    for expr_str in expressions:
        try:
            clean_str = sanitize_expression(expr_str)
            expr = parse_expr(clean_str, transformations=transformations)
            result = expr.evalf()
            print(f"Input: {expr_str:10} | Clean: {clean_str:10} | Result: {result}")
        except Exception as e:
            print(f"Input: {expr_str:10} | Error: {e}")

if __name__ == "__main__":
    test_multiplication()
