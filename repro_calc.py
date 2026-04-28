import sympy
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application

def test_multiplication():
    transformations = (standard_transformations + (implicit_multiplication_application,))
    
    expressions = [
        "2*3",
        "2(3)",
        "2x",
        "2 * 3",
        "2 × 3"
    ]
    
    for expr_str in expressions:
        try:
            # Emulate sanitize_expression
            clean_str = expr_str.replace('×', '*')
            
            expr = parse_expr(clean_str, transformations=transformations)
            result = expr.evalf()
            print(f"Input: {expr_str} -> Parsed: {expr} -> Result: {result}")
        except Exception as e:
            print(f"Input: {expr_str} -> Error: {e}")

if __name__ == "__main__":
    test_multiplication()
