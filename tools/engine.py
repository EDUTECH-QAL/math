import sympy
from sympy import symbols, solve, Eq, factor, expand, simplify, latex as sympy_latex, Rational, oo, S, sympify, sqrt, Abs, degree
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application

# Custom latex function to use \times for multiplication
def latex(expr, **kwargs):
    if 'mul_symbol' not in kwargs:
        kwargs['mul_symbol'] = 'times'
    return sympy_latex(expr, **kwargs)
import random
import math
import re

def get_math_config(angle_unit='RAD'):
    """
    Returns consistent transformations and local_dict for SymPy parsing.
    """
    transformations = (standard_transformations + (implicit_multiplication_application,))
    
    local_dict = {
        'log': lambda x: sympy.log(x, 10),
        'ln': sympy.log,
        'e': sympy.E,
        'pi': sympy.pi
    }
    
    if str(angle_unit).upper() == 'DEG':
        local_dict.update({
            'sin': lambda x: sympy.sin(sympy.pi*x/180),
            'cos': lambda x: sympy.cos(sympy.pi*x/180),
            'tan': lambda x: sympy.tan(sympy.pi*x/180),
            'cot': lambda x: sympy.cot(sympy.pi*x/180),
            'sec': lambda x: sympy.sec(sympy.pi*x/180),
            'csc': lambda x: sympy.csc(sympy.pi*x/180),
        })
    
    return transformations, local_dict

def sanitize_expression(expr_str):
    """
    Sanitizes the input expression string for SymPy.
    Replaces common non-standard mathematical symbols.
    """
    if not expr_str:
        return ""
    
    # Replace common multiplication 'x' or 'X' between numbers or parentheses
    # This handles cases like '5 x 5', '5X5', '5 x (2)', '(2) x 5', '(2) x (2)'
    expr_str = re.sub(r'(\d|\))\s*[xX]\s*(\d|\()', r'\1*\2', expr_str)
    
    # Replace caret with double asterisk for power
    expr_str = expr_str.replace('^', '**')
    # Replace division symbol
    expr_str = expr_str.replace('÷', '/')
    expr_str = expr_str.replace('×', '*')
    expr_str = expr_str.replace('\\times', '*')
    expr_str = expr_str.replace('·', '*') # Middle dot multiplication
    expr_str = expr_str.replace('∗', '*') # Asterisk operator (U+2217)
    
    # Replace dot with spaces around it as multiplication (e.g., '5 . 5')
    # but don't touch decimal points like '5.5'
    expr_str = re.sub(r'(\d|\))\s+\.\s+(\d|\()', r'\1*\2', expr_str)
    
    expr_str = expr_str.replace('≤', '<=')
    expr_str = expr_str.replace('≥', '>=')
    
    # Handle absolute value |x| -> Abs(x)
    if '|' in expr_str:
        expr_str = re.sub(r'\|([^|]+)\|', r'Abs(\1)', expr_str)
        
    return expr_str

def safe_sympify(expr_str, angle_unit='RAD'):
    """
    Safely parses a math expression string into a SymPy expression.
    """
    if not expr_str: return None
    clean_str = sanitize_expression(expr_str)
    transformations, local_dict = get_math_config(angle_unit)
    return parse_expr(clean_str, transformations=transformations, local_dict=local_dict)

def to_eq(s, angle_unit='RAD'):
    """
    Parses a string that may contain '=' into a SymPy Eq object.
    """
    if not s or not str(s).strip(): 
        raise ValueError("Empty input")
        
    s_clean = sanitize_expression(s)
    if not s_clean.strip():
        raise ValueError("Invalid input")

    if '=' in s_clean:
        parts = s_clean.split('=')
        if len(parts) != 2 or not parts[0].strip() or not parts[1].strip():
            raise ValueError("Invalid equation format")
        lhs = safe_sympify(parts[0], angle_unit)
        rhs = safe_sympify(parts[1], angle_unit)
        if lhs is None or rhs is None:
            raise ValueError("Could not parse equation sides")
        return Eq(lhs, rhs)
    else:
        # Treat as expression = 0
        expr = safe_sympify(s_clean, angle_unit)
        if expr is None:
            raise ValueError("Could not parse expression")
        return Eq(expr, 0)

def calculate_expression(expression, config={}, lang='en'):
    """
    Evaluates a mathematical expression.
    """
    try:
        err_msg = "Invalid Expression" if lang == 'en' else "تعبير غير صالح"
        if not expression: return {'error': err_msg}
        
        angle_unit = (config or {}).get('angle_unit', 'RAD')
        clean_str = sanitize_expression(expression)
        transformations, local_dict = get_math_config(angle_unit)
        
        expr = parse_expr(clean_str, transformations=transformations, local_dict=local_dict)
        result = expr.evalf()
        
        # Clean up result formatting
        if result.is_number:
            try:
                # Use sympy's evalf for initial check but handle precision carefully
                if result.is_Integer:
                    return {'result': str(result), 'latex': latex(expr)}
                
                f_val = float(result)
                if f_val.is_integer():
                    res_str = str(int(f_val))
                else:
                    # Remove trailing zeros and avoid scientific notation for small/large numbers
                    res_str = f"{f_val:g}"
                
                # Double check for scientific notation or artifacts
                if 'e' in res_str.lower() or '*' in res_str:
                    res_str = str(result)
                
                # Replace * with × for clean display in math-field
                res_str = res_str.replace('*', '×')
                
                return {'result': res_str, 'latex': latex(expr)}
            except:
                pass
                
        # For non-numbers (expressions with variables), use simplify and string conversion
        res_str = str(result)
        # Final cleanup for any leftover multiplication stars in simple outputs
        res_str = res_str.replace('*', '×')
        
        if res_str.replace('.', '').replace('-', '').replace('×', '').isdigit():
            # If it's a numeric string with maybe a dot, minus, or ×, we're good
            pass
        elif '×' in res_str:
             # Check if it's a numeric expression that didn't fully evaluate for some reason
             try:
                 # Try one last evalf if stars are present in what should be a number
                 eval_res = result.evalf(chop=True)
                 if eval_res.is_number:
                     res_str = f"{float(eval_res):g}"
             except:
                 pass

        return {'result': res_str, 'latex': latex(expr)}
    except Exception as e:
        return {'error': str(e)}

def solve_equation_step_by_step(equation_str, lang='en'):
    """
    Solves linear, quadratic, and exponential equations with steps.
    """
    phrases = {
        'en': {
            'step': 'Step', 'solution': 'Solution', 'rewrite': 'Rewrite equation', 
            'isolate': 'Isolate variable', 'factor': 'Factorize', 'roots': 'Roots',
            'check': 'Check', 'exponential': 'Exponential Equation'
        },
        'ar': {
            'step': 'خطوة', 'solution': 'الحل', 'rewrite': 'إعادة كتابة المعادلة', 
            'isolate': 'عزل المتغير', 'factor': 'التحليل', 'roots': 'الجذور',
            'check': 'التحقق', 'exponential': 'معادلة أسية'
        }
    }
    t = phrases.get(lang, phrases['en'])
    
    if not equation_str or not str(equation_str).strip():
        msg = "الرجاء إدخال معادلة صحيحة" if lang == 'ar' else "Please enter a valid equation"
        return {'error': msg}

    steps = []
    try:
        if '>' in equation_str or '<' in equation_str:
            res = solve_inequality_steps(equation_str, lang=lang)
            return res

        if '=' not in equation_str:
             equation_str += " = 0"
        
        parts = equation_str.split('=')
        if len(parts) != 2:
            return {'error': 'Invalid equation format'}
            
        if not parts[0].strip() or not parts[1].strip():
             msg = "الرجاء إدخال معادلة كاملة" if lang == 'ar' else "Please enter a complete equation"
             return {'error': msg}

        lhs = safe_sympify(parts[0])
        rhs = safe_sympify(parts[1])
        eq = Eq(lhs, rhs)
        
        free_symbols = list(eq.free_symbols)
        x = free_symbols[0] if free_symbols else symbols('x')
        
        steps.append(f"{t['rewrite']}: ${latex(eq)}$")

        # Handle numeric-only equation (no variables)
        if len(free_symbols) == 0:
            diff_val = simplify(lhs - rhs)
            if diff_val == 0:
                all_reals = "All real numbers" if lang == 'en' else "جميع الأعداد الحقيقية"
                steps.append(f"{t['check']}: $0 = 0$")
                return {'latex': all_reals, 'steps': steps}
            else:
                no_sol = "No solution" if lang == 'en' else "لا يوجد حل"
                steps.append(f"{t['check']}: ${latex(diff_val)} \\ne 0$")
                return {'latex': no_sol, 'steps': steps}

        # Check for exponential equation (Grade 8 Term 2)
        # Simple heuristic: variable in exponent
        is_exponential = any(s == x for term in sympy.preorder_traversal(lhs) for s in term.free_symbols if term.is_Pow and term.exp.has(x)) or \
                         any(s == x for term in sympy.preorder_traversal(rhs) for s in term.free_symbols if term.is_Pow and term.exp.has(x))
        
        if is_exponential:
            steps.append(f"**{t['exponential']}**")
            # Try to rewrite as base^A = base^B
            # This is a bit complex to do generically, but we can try to simplify both sides
            lhs_simp = simplify(lhs)
            rhs_simp = simplify(rhs)
            
            if lhs_simp != lhs or rhs_simp != rhs:
                steps.append(f"{t['rewrite']}: ${latex(Eq(lhs_simp, rhs_simp))}$")
            
            # If form is b^f(x) = b^k
            # Attempt to extract bases (very basic check)
            if lhs_simp.is_Pow and rhs_simp.is_Pow and lhs_simp.base == rhs_simp.base:
                steps.append(f"Since bases are equal (${latex(lhs_simp.base)}$), exponents must be equal:")
                steps.append(f"${latex(lhs_simp.exp)} = {latex(rhs_simp.exp)}$")
                eq = Eq(lhs_simp.exp, rhs_simp.exp)
            elif lhs_simp.is_Pow and not rhs_simp.is_Pow:
                # Try to write RHS as power of LHS base
                base = lhs_simp.base
                try:
                    rhs_log = sympy.log(rhs_simp, base)
                    if rhs_log.is_integer:
                         steps.append(f"Rewrite ${latex(rhs_simp)}$ as ${latex(base)}^{{{latex(rhs_log)}}}$")
                         steps.append(f"${latex(lhs_simp)} = {latex(base)}^{{{latex(rhs_log)}}}$")
                         steps.append(f"${latex(lhs_simp.exp)} = {latex(rhs_log)}$")
                         eq = Eq(lhs_simp.exp, rhs_log)
                except:
                    pass

        # Move everything to LHS for standard form (if not processed as exponential)
        if not is_exponential:
            eq_zero = Eq(lhs - rhs, 0)
            steps.append(f"{t['rewrite']} ($=0$): ${latex(eq_zero)}$")
            
            # Try factorization first (Grade 8 requirement)
            expr = lhs - rhs
            factored = factor(expr)
            
            if factored != expr:
                steps.append(f"{t['factor']}: ${latex(Eq(factored, 0))}$")
        
        solutions = solve(eq, x)
        
        sol_latex_list = []
        plot_data = None
        
        # No solution case
        if isinstance(solutions, list) and len(solutions) == 0:
            no_sol = "No solution" if lang == 'en' else "لا يوجد حل"
            steps.append(f"{t['check']}: {no_sol}")
            return {'latex': no_sol, 'steps': steps}
        
        for s in solutions:
            sol_latex_list.append(latex(s))
            
        sol_latex = ', '.join(sol_latex_list)
        
        # Simple plot data for single real solution
        if len(solutions) == 1 and getattr(solutions[0], 'is_real', False):
             try:
                val = float(solutions[0])
                plot_data = {'val': val, 'direction': 'none', 'inclusive': True}
             except:
                pass
                
        return {'latex': f"{latex(x)} \\in \\{{{sol_latex}\\}}", 'steps': steps, 'plot_data': plot_data}
    except Exception as e:
        return {'error': str(e)}

def expand_algebraic_expression(expression_str, lang='en'):
    try:
        expr = safe_sympify(expression_str)
        expanded = expand(expr)
        steps = [f"Original: ${latex(expr)}$", f"Expanded: ${latex(expanded)}$"]
        return {'latex': latex(expanded), 'steps': steps}
    except Exception as e:
        return {'error': str(e)}

def polynomial_long_division_steps(dividend_str, divisor_str, lang='en'):
    try:
        dividend = safe_sympify(dividend_str)
        divisor = safe_sympify(divisor_str)
        
        if divisor is None:
            return {'error': 'Invalid divisor'}
        if simplify(divisor) == 0:
            return {'error': 'Division by zero'}
        
        q, r = sympy.div(dividend, divisor)
        steps = [
            f"Divide ${latex(dividend)}$ by ${latex(divisor)}$",
            f"Quotient: ${latex(q)}$",
            f"Remainder: ${latex(r)}$",
        ]
        result_latex = f"{latex(q)}"
        if simplify(r) != 0:
            steps.append(f"Result: ${latex(q)} + \\frac{{{latex(r)}}}{{{latex(divisor)}}}$")
            result_latex = f"{latex(q)} + \\frac{{{latex(r)}}}{{{latex(divisor)}}}"
        else:
            steps.append("Result: (Exact division, remainder = 0)")
        
        return {
            'latex': result_latex,
            'steps': steps,
            'quotient_latex': latex(q),
            'remainder_latex': latex(r)
        }
    except Exception as e:
        return {'error': str(e)}

def simplify_exponents_steps(expression_str, lang='en'):
    try:
        expr = safe_sympify(expression_str)
        simplified = simplify(expr)
        steps = [f"Original: ${latex(expr)}$", f"Simplified: ${latex(simplified)}$"]
        return {'latex': latex(simplified), 'steps': steps}
    except Exception as e:
        return {'error': str(e)}

def solve_inequality_steps(ineq_str, lang='en'):
    phrases = {
        'en': {'rewrite': 'Rewrite', 'factor': 'Factorize', 'solution': 'Solution'},
        'ar': {'rewrite': 'إعادة كتابة', 'factor': 'التحليل', 'solution': 'مجموعة الحل'}
    }
    t = phrases.get(lang, phrases['en'])
    try:
        if not ineq_str or not str(ineq_str).strip():
            msg = "Invalid inequality" if lang == 'en' else "متباينة غير صالحة"
            return {'error': msg}
        s = sanitize_expression(ineq_str)
        op = None
        for cand in ['<=', '>=', '<', '>']:
            if cand in s:
                op = cand
                break
        if not op:
            return {'error': 'Invalid inequality'}
        parts = s.split(op)
        if len(parts) != 2:
            return {'error': 'Invalid inequality'}
        lhs = safe_sympify(parts[0])
        rhs = safe_sympify(parts[1])
        expr = simplify(lhs - rhs)
        syms = list(expr.free_symbols)
        x = syms[0] if syms else symbols('x')
        steps = []
        rel_text = f"${latex(expr)}\\ {op}\\ 0$"
        steps.append(f"{t['rewrite']}: {rel_text}")
        fct = factor(expr)
        if fct != expr:
            steps.append(f"{t['factor']}: ${latex(fct)}\\ {op}\\ 0$")
        if op == '<':
            rel = expr < 0
        elif op == '>':
            rel = expr > 0
        elif op == '<=':
            rel = expr <= 0
        else:
            rel = expr >= 0
        sol = sympy.solve_univariate_inequality(rel, x, relational=False)
        sol_latex = latex(sol)
        steps.append(f"{t['solution']}: ${sol_latex}$")
        return {'latex': sol_latex, 'steps': steps}
    except Exception as e:
        return {'error': str(e)}

def convert_scientific_notation(value_str, lang='en'):
    phrases = {
        'en': {
            'value': 'Original Value',
            'scientific': 'Scientific Notation',
            'decimal': 'Decimal Form'
        },
        'ar': {
            'value': 'القيمة الأصلية',
            'scientific': 'الصورة القياسية (العلمية)',
            'decimal': 'الصورة العشرية'
        }
    }
    t = phrases.get(lang, phrases['en'])
    try:
        # Check if the input is in scientific notation already (e.g., 5e-4 or 5*10^-4)
        clean_str = str(value_str).replace('\\times', '*').replace('^', '**').replace('{', '').replace('}', '')
        
        # Try to parse using sympy for expressions like 5*10**-4
        val_expr = safe_sympify(clean_str)
        val = float(val_expr.evalf())
        
        sci = "{:.2e}".format(val)
        base, exponent = sci.split('e')
        # Remove trailing zeros from base
        base = float(base)
        if base == int(base):
            base = int(base)
        
        latex_sci = f"{base} \\times 10^{{{int(exponent)}}}"
        
        # Format decimal form to avoid scientific notation
        if abs(val) < 1 and val != 0:
            decimal_form = f"{val:.10f}".rstrip('0').rstrip('.')
        else:
            decimal_form = f"{val:g}"
            
        steps = [
            f"{t['value']}: ${latex(val_expr)}$",
            f"{t['decimal']}: {decimal_form}",
            f"{t['scientific']}: ${latex_sci}$"
        ]
        return {'latex': latex_sci, 'steps': steps}
    except Exception as e:
        if lang == 'ar':
            return {'error': "خطأ: تعذر تحويل القيمة. تأكد من إدخال رقم صحيح أو صيغة رياضية صالحة."}
        return {'error': f"Error: could not convert value. {str(e)}"}

def factorize_expression_steps(expression_str, lang='en'):
    phrases = {
        'en': {
            'original': 'Original Expression', 
            'factor': 'Factored Form', 
            'method': 'Method',
            'common_factor': 'Highest Common Factor (HCF)',
            'diff_squares': 'Difference of Two Squares',
            'sum_cubes': 'Sum of Two Cubes',
            'diff_cubes': 'Difference of Two Cubes',
            'trinomial': 'Trinomial Factorization',
            'grouping': 'Factorization by Grouping',
            'identify': 'Identifying the pattern',
            'step': 'Step'
        },
        'ar': {
            'original': 'المقدار الأصلي', 
            'factor': 'الصورة التحليلية', 
            'method': 'الطريقة',
            'common_factor': 'إخراج العامل المشترك الأعلى (ع.م.أ)',
            'diff_squares': 'الفرق بين مربعين',
            'sum_cubes': 'مجموع مكعبين',
            'diff_cubes': 'الفرق بين مكعبين',
            'trinomial': 'تحليل المقدار الثلاثي',
            'grouping': 'التحليل بالتقسيم',
            'identify': 'تحديد النمط',
            'step': 'خطوة'
        }
    }
    t = phrases.get(lang, phrases['en'])
    try:
        if not expression_str or not str(expression_str).strip():
            msg = "Please enter an expression" if lang == 'en' else "الرجاء إدخال مقدار"
            return {'error': msg}
        clean = sanitize_expression(expression_str)
        # Detect equation/inequality and rewrite to expression before parsing
        op = None
        for cand in ['<=', '>=', '<', '>', '=']:
            if cand in clean:
                op = cand
                break
        steps = []
        expr_to_factor = None
        if op:
            parts = clean.split(op)
            if len(parts) == 2 and parts[0].strip() and parts[1].strip():
                lhs = safe_sympify(parts[0])
                rhs = safe_sympify(parts[1])
                expr_to_factor = simplify(lhs - rhs)
                steps.append(f"{t['rewrite'] if 'rewrite' in t else 'Rewrite'}: ${latex(expr_to_factor)}$")
            else:
                return {'error': "Invalid input" if lang == 'en' else "مدخل غير صالح"}
        else:
            expr = safe_sympify(clean)
            expr_to_factor = expr
            steps.append(f"{t['original']}: ${latex(expr_to_factor)}$")
        
        # 1. Check for Common Factor
        terms = list(sympy.Add.make_args(expr_to_factor))
        common = sympy.gcd(terms)
        if common != 1:
            steps.append(f"{t['common_factor']}: {latex(common)}")
            fact_tmp = factor(expr_to_factor)
            steps.append(f"${latex(common)} ({latex(fact_tmp/common)})$")
        
        factored = factor(expr_to_factor)
        
        # Try to guess method based on expression structure
        if expr_to_factor.is_Add and len(terms) == 2:
            # Check signs
            c1, c2 = terms[0], terms[1]
            if (c1.is_Mul and c1.as_coeff_Mul()[0] < 0) or (c2.is_Mul and c2.as_coeff_Mul()[0] < 0):
                steps.append(f"{t['identify']}: {t['diff_squares']}")
            elif degree(expr_to_factor) == 3:
                steps.append(f"{t['identify']}: {t['sum_cubes']} / {t['diff_cubes']}")
        elif expr_to_factor.is_Add and len(terms) == 3:
             if degree(expr_to_factor) == 2:
                 steps.append(f"{t['identify']}: {t['trinomial']}")
        elif expr_to_factor.is_Add and len(terms) == 4:
             steps.append(f"{t['identify']}: {t['grouping']}")

        if factored != expr_to_factor:
             steps.append(f"{t['factor']}: ${latex(factored)}$")
        else:
             steps.append(f"{t['factor']}: (Already simplified)")

        return {'latex': latex(factored), 'steps': steps}
    except Exception as e:
        return {'error': str(e)}

def pythagoras_converse(a, b, c, lang='en'):
    phrases = {
        'en': {'sides': 'Sides', 'check': 'Checking', 'right': 'Right Angled', 'acute': 'Acute Angled', 'obtuse': 'Obtuse Angled', 'reason': 'Reason'},
        'ar': {'sides': 'الأضلاع', 'check': 'التحقق', 'right': 'قائم الزاوية', 'acute': 'حاد الزوايا', 'obtuse': 'منفرج الزاوية', 'reason': 'السبب'}
    }
    t = phrases.get(lang, phrases['en'])
    try:
        sides = sorted([float(a), float(b), float(c)])
        x, y, z = sides[0], sides[1], sides[2]
        
        steps = [f"{t['sides']}: {x}, {y}, {z}"]
        steps.append(f"Compare $z^2$ with $x^2 + y^2$")
        
        z2 = z**2
        xy2 = x**2 + y**2
        
        steps.append(f"${z}^2 = {z2}$")
        steps.append(f"${x}^2 + {y}^2 = {xy2}$")
        
        result = ""
        if abs(z2 - xy2) < 1e-9:
            result = t['right']
            steps.append(f"Since $z^2 = x^2 + y^2$, Triangle is **{result}**")
        elif z2 > xy2:
            result = t['obtuse']
            steps.append(f"Since $z^2 > x^2 + y^2$, Triangle is **{result}**")
        else:
            result = t['acute']
            steps.append(f"Since $z^2 < x^2 + y^2$, Triangle is **{result}**")
            
        return {'result': result, 'steps': steps}
    except Exception as e:
        return {'error': str(e)}

def quadrilateral_area(shape_type, params, lang='en'):
    """
    Calculates area of quadrilaterals (Rhombus, Trapezoid, Square) with steps.
    """
    phrases = {
        'en': {
            'square': 'Square', 'rhombus': 'Rhombus', 'trapezoid': 'Trapezoid',
            'diagonal': 'Diagonal', 'base': 'Base', 'height': 'Height',
            'median': 'Median Base', 'area_formula': 'Area Formula',
            'substitute': 'Substitution', 'result': 'Area', 'd1': 'Diagonal 1', 'd2': 'Diagonal 2'
        },
        'ar': {
            'square': 'المربع', 'rhombus': 'المعين', 'trapezoid': 'شبه المنحرف',
            'diagonal': 'القطر', 'base': 'القاعدة', 'height': 'الارتفاع',
            'median': 'القاعدة المتوسطة', 'area_formula': 'قانون المساحة',
            'substitute': 'التعويض', 'result': 'المساحة', 'd1': 'القطر 1', 'd2': 'القطر 2'
        }
    }
    t = phrases.get(lang, phrases['en'])
    steps = []
    
    try:
        if not params:
            params = {}
            
        area = 0
        if shape_type == 'square':
            d = float(params.get('diagonal', 0))
            steps.append(f"{t['square']} ({t['diagonal']} = {d})")
            steps.append(f"{t['area_formula']}: $A = \\frac{{1}}{{2}} d^2$")
            area = 0.5 * (d**2)
            steps.append(f"{t['substitute']}: $A = 0.5 \\times ({d})^2 = 0.5 \\times {d**2}$")
            
        elif shape_type == 'rhombus':
            d1 = float(params.get('d1', 0))
            d2 = float(params.get('d2', 0))
            steps.append(f"{t['rhombus']} ({t['d1']}={d1}, {t['d2']}={d2})")
            steps.append(f"{t['area_formula']}: $A = \\frac{{1}}{{2}} d_1 \\times d_2$")
            area = 0.5 * d1 * d2
            steps.append(f"{t['substitute']}: $A = 0.5 \\times {d1} \\times {d2}$")
            
        elif shape_type == 'trapezoid':
            h = float(params.get('h', 0))
            if 'm' in params and params['m']:
                m = float(params.get('m', 0))
                steps.append(f"{t['trapezoid']} ({t['median']}={m}, {t['height']}={h})")
                steps.append(f"{t['area_formula']}: $A = \\text{{{t['median']}}} \\times \\text{{{t['height']}}}$")
                area = m * h
                steps.append(f"{t['substitute']}: $A = {m} \\times {h}$")
            else:
                b1 = float(params.get('b1', 0))
                b2 = float(params.get('b2', 0))
                steps.append(f"{t['trapezoid']} (b1={b1}, b2={b2}, h={h})")
                steps.append(f"{t['area_formula']}: $A = \\frac{{b_1 + b_2}}{{2}} \\times h$")
                area = 0.5 * (b1 + b2) * h
                steps.append(f"{t['substitute']}: $A = \\frac{{{b1} + {b2}}}{{2}} \\times {h}$")
        
        steps.append(f"{t['result']}: ${area}$")
        return {'result': area, 'steps': steps}
        
    except Exception as e:
        return {'error': str(e)}

def probability_simulator(sim_type, trials=1, lang='en'):
    results = {}
    theoretical = {}
    
    if sim_type == 'coin':
        space = ['Head', 'Tail']
        theoretical = {'Head': 0.5, 'Tail': 0.5}
    elif sim_type == 'dice':
        space = ['1', '2', '3', '4', '5', '6']
        prob = 1.0/6.0
        theoretical = {k: prob for k in space}
    elif sim_type == 'cards':
        space = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
        prob = 0.25
        theoretical = {k: prob for k in space}
    else:
        return {'error': 'Invalid type'}

    for _ in range(trials):
        res = random.choice(space)
        results[res] = results.get(res, 0) + 1
            
    response_probs = {}
    for key in space:
        response_probs[key] = {'theoretical': theoretical[key]}
        
    return {
        'total_trials': trials,
        'results': results,
        'probabilities': response_probs
    }

def geometry_transform(ttype, params, lang='en'):
    phrases = {
        'en': {
            'translate': 'Translation',
            'rotate': 'Rotation',
            'reflect': 'Reflection',
            'scale': 'Dilation',
            'result': 'Result',
            'point': 'Point',
            'center': 'Center',
            'angle': 'Angle',
            'factor': 'Scale factor'
        },
        'ar': {
            'translate': 'إزاحة',
            'rotate': 'دوران',
            'reflect': 'انعكاس',
            'scale': 'توسع',
            'result': 'النتيجة',
            'point': 'نقطة',
            'center': 'مركز',
            'angle': 'زاوية',
            'factor': 'عامل التوسع'
        }
    }
    t = phrases.get(lang, phrases['en'])
    try:
        x = float(params.get('x'))
        y = float(params.get('y'))
        steps = []
        res = None
        plot = []
        if ttype == 'translate':
            dx = float(params.get('dx', 0))
            dy = float(params.get('dy', 0))
            nx = x + dx
            ny = y + dy
            steps.append(f"{t['translate']}: ({x}, {y}) → ({nx}, {ny})")
            res = {'x': nx, 'y': ny}
        elif ttype == 'rotate':
            angle = float(params.get('angle', 0))
            cx = float(params.get('cx', 0))
            cy = float(params.get('cy', 0))
            rad = math.pi * angle / 180.0
            tx = x - cx
            ty = y - cy
            rx = tx * math.cos(rad) - ty * math.sin(rad)
            ry = tx * math.sin(rad) + ty * math.cos(rad)
            nx = rx + cx
            ny = ry + cy
            steps.append(f"{t['rotate']}: {t['point']} ({x}, {y}), {t['center']} ({cx}, {cy}), {t['angle']} {angle}°")
            steps.append(f"{t['result']}: ({nx}, {ny})")
            res = {'x': nx, 'y': ny}
        elif ttype == 'reflect':
            axis = params.get('axis', 'x')
            if axis == 'x':
                nx, ny = x, -y
            elif axis == 'y':
                nx, ny = -x, y
            elif axis == 'y=x':
                nx, ny = y, x
            elif axis == 'y=-x':
                nx, ny = -y, -x
            else:
                nx, ny = x, y
            steps.append(f"{t['reflect']}: {axis}")
            steps.append(f"{t['result']}: ({nx}, {ny})")
            res = {'x': nx, 'y': ny}
        elif ttype == 'scale':
            k = float(params.get('k', 1))
            cx = float(params.get('cx', 0))
            cy = float(params.get('cy', 0))
            nx = cx + k * (x - cx)
            ny = cy + k * (y - cy)
            steps.append(f"{t['scale']}: {t['factor']} {k}, {t['center']} ({cx}, {cy})")
            steps.append(f"{t['result']}: ({nx}, {ny})")
            res = {'x': nx, 'y': ny}
        plot = [{'x': x, 'y': y}, {'x': res['x'], 'y': res['y']}]
        return {'result': res, 'steps': steps, 'plot_data': plot}
    except Exception as e:
        return {'error': str(e)}

def statistics_summary(values, lang='en'):
    phrases = {
        'en': {
            'count': 'Count', 'min': 'Min', 'max': 'Max', 'range': 'Range',
            'mean': 'Mean', 'median': 'Median', 'mode': 'Mode',
            'q1': 'Q1', 'q3': 'Q3', 'iqr': 'IQR',
            'pvar': 'Population Variance', 'pstd': 'Population Std Dev',
            'svar': 'Sample Variance', 'sstd': 'Sample Std Dev'
        },
        'ar': {
            'count': 'العدد', 'min': 'الصغرى', 'max': 'الكبرى', 'range': 'المدى',
            'mean': 'المتوسط', 'median': 'الوسيط', 'mode': 'النمط',
            'q1': 'الربع Q1', 'q3': 'الربع Q3', 'iqr': 'المدى بين الربعيين',
            'pvar': 'التباين (مجتمع)', 'pstd': 'الانحراف المعياري (مجتمع)',
            'svar': 'التباين (عينة)', 'sstd': 'الانحراف المعياري (عينة)'
        }
    }
    t = phrases.get(lang, phrases['en'])
    try:
        arr = [float(x) for x in values]
        n = len(arr)
        if n == 0:
            msg = "Please provide data values" if lang == 'en' else "يرجى إدخال بيانات"
            return {'error': msg}
        arr_sorted = sorted(arr)
        mn = arr_sorted[0]
        mx = arr_sorted[-1]
        rng = mx - mn
        mean = sum(arr) / n
        mid = n // 2
        if n % 2 == 1:
            median = arr_sorted[mid]
            lower = arr_sorted[:mid]
            upper = arr_sorted[mid+1:]
        else:
            median = (arr_sorted[mid-1] + arr_sorted[mid]) / 2
            lower = arr_sorted[:mid]
            upper = arr_sorted[mid:]
        def median_of(a):
            m = len(a) // 2
            if len(a) == 0: return None
            if len(a) % 2 == 1:
                return a[m]
            return (a[m-1] + a[m]) / 2
        q1 = median_of(lower)
        q3 = median_of(upper)
        iqr = None if (q1 is None or q3 is None) else (q3 - q1)
        freq = {}
        for v in arr_sorted:
            freq[v] = freq.get(v, 0) + 1
        maxf = max(freq.values())
        modes = [v for v, c in freq.items() if c == maxf]
        mean_diff_sq = [(x-mean)**2 for x in arr]
        pvar = sum(mean_diff_sq) / n
        pstd = math.sqrt(pvar)
        svar = sum(mean_diff_sq) / (n-1) if n > 1 else 0.0
        sstd = math.sqrt(svar)
        steps = [
            f"{t['count']}: {n}",
            f"{t['min']}: {mn}",
            f"{t['max']}: {mx}",
            f"{t['range']}: {rng}",
            f"{t['mean']}: {mean}",
            f"{t['median']}: {median}",
            f"{t['mode']}: {', '.join(map(str, modes))}",
        ]
        if q1 is not None and q3 is not None:
            steps += [f"{t['q1']}: {q1}", f"{t['q3']}: {q3}", f"{t['iqr']}: {iqr}"]
        steps += [f"{t['pvar']}: {pvar}", f"{t['pstd']}: {pstd}", f"{t['svar']}: {svar}", f"{t['sstd']}: {sstd}"]
        result = {
            'count': n, 'min': mn, 'max': mx, 'range': rng,
            'mean': mean, 'median': median, 'modes': modes,
            'q1': q1, 'q3': q3, 'iqr': iqr,
            'population_variance': pvar, 'population_std': pstd,
            'sample_variance': svar, 'sample_std': sstd
        }
        return {'result': result, 'steps': steps}
    except Exception as e:
        return {'error': str(e)}

def statistics_frequency(values, bins=None, lang='en'):
    phrases = {
        'en': {'classes': 'Classes', 'width': 'Class Width', 'freq': 'Frequency'},
        'ar': {'classes': 'الفئات', 'width': 'عرض الفئة', 'freq': 'التكرار'}
    }
    t = phrases.get(lang, phrases['en'])
    try:
        arr = [float(x) for x in values]
        n = len(arr)
        if n == 0:
            msg = "Please provide data values" if lang == 'en' else "يرجى إدخال بيانات"
            return {'error': msg}
        mn = min(arr); mx = max(arr)
        k = int(bins) if bins else math.ceil(1 + math.log2(n))
        width = (mx - mn) / k if k > 0 else (mx - mn)
        classes = []
        freqs = []
        for i in range(k):
            a = mn + i * width
            b = mn + (i + 1) * width
            classes.append((a, b))
            count = sum(1 for v in arr if (v >= a and (i == k-1 or v < b)))
            freqs.append(count)
        steps = [f"{t['classes']}: {k}", f"{t['width']}: {width}"]
        table = [{'from': a, 'to': b, 'freq': f} for (a,b), f in zip(classes, freqs)]
        return {'result': table, 'steps': steps}
    except Exception as e:
        return {'error': str(e)}

def statistics_correlation(x_values, y_values, lang='en'):
    phrases = {
        'en': {'corr': 'Pearson Correlation', 'meanx': 'Mean X', 'meany': 'Mean Y'},
        'ar': {'corr': 'معامل الارتباط بيرسون', 'meanx': 'متوسط س', 'meany': 'متوسط ص'}
    }
    t = phrases.get(lang, phrases['en'])
    try:
        xs = [float(x) for x in x_values]
        ys = [float(y) for y in y_values]
        if len(xs) != len(ys) or len(xs) < 2:
            msg = "Provide equal-length datasets (>=2)" if lang == 'en' else "يرجى إدخال مجموعتين متساويتين بالطول (2 فأكثر)"
            return {'error': msg}
        n = len(xs)
        mx = sum(xs)/n
        my = sum(ys)/n
        num = sum((x-mx)*(y-my) for x,y in zip(xs,ys))
        denx = math.sqrt(sum((x-mx)**2 for x in xs))
        deny = math.sqrt(sum((y-my)**2 for y in ys))
        r = num / (denx * deny) if denx > 0 and deny > 0 else 0.0
        steps = [f"{t['meanx']}: {mx}", f"{t['meany']}: {my}", f"{t['corr']}: {r}"]
        return {'result': r, 'steps': steps}
    except Exception as e:
        return {'error': str(e)}

def solve_linear_system_steps(eq1_str, eq2_str, lang='en'):
    phrases = {
        'en': {
            'step': 'Step',
            'isolate': 'Isolate',
            'sub': 'Substitute',
            'solve': 'Solve',
            'result': 'Solution',
            'error_title': 'Input Error:',
            'error_msg': 'This tool solves systems of two linear equations in x and y only.\nPlease enter two valid equations such as:\nx + y = 4\n2x - y = 3'
        },
        'ar': {
            'step': 'خطوة',
            'isolate': 'عزل',
            'sub': 'التعويض',
            'solve': 'حل',
            'result': 'مجموعة الحل',
            'error_title': 'خطأ في الإدخال:',
            'error_msg': 'هذه الأداة تحل نظامين من المعادلات الخطية في متغيرين x و y فقط.\nيرجى إدخال معادلتين في x و y مثل:\nx + y = 4\n2x - y = 3'
        }
    }
    t = phrases.get(lang, phrases['en'])
    
    try:
        # Parsing with '=' support
        eq1 = to_eq(eq1_str)
        eq2 = to_eq(eq2_str)

        # Standardize: LHS - RHS = 0
        eq1_std = eq1.lhs - eq1.rhs
        eq2_std = eq2.lhs - eq2.rhs
        
        syms = list(eq1_std.free_symbols.union(eq2_std.free_symbols))
        syms.sort(key=lambda s: str(s))
        
        # Require exactly two variables for linear system
        if len(syms) != 2:
            msg = f"{t['error_title']}\n{t['error_msg']}"
            return {'error': msg}
        
        # Validate linearity (total degree == 1)
        try:
            p1 = sympy.Poly(eq1_std, syms)
            p2 = sympy.Poly(eq2_std, syms)
            if p1.total_degree() > 1 or p2.total_degree() > 1:
                if lang == 'ar':
                    msg = (
                        "خطأ في الإدخال:\n"
                        "هذه الأداة تحل نظامين من المعادلات الخطية في متغيرين x و y فقط.\n"
                        "يبدو أن الإدخال يحتوي على تعبيرات غير خطية.\n"
                        "يرجى إدخال معادلات صحيحة مثل:\n"
                        "x + y = 4\n"
                        "2x - y = 3"
                    )
                else:
                    msg = (
                        "Input Error:\n"
                        "This tool solves systems of two linear equations in x and y only.\n"
                        "Your input contains non-linear expressions.\n"
                        "Please enter valid equations such as:\n"
                        "x + y = 4\n"
                        "2x - y = 3"
                    )
                return {'error': msg}
        except Exception:
            # If Poly fails, treat as non-linear
            if lang == 'ar':
                msg = (
                    "خطأ في الإدخال:\n"
                    "هذه الأداة تحل نظامين من المعادلات الخطية في متغيرين x و y فقط.\n"
                    "يبدو أن الإدخال يحتوي على تعبيرات غير خطية.\n"
                    "يرجى إدخال معادلات صحيحة مثل:\n"
                    "x + y = 4\n"
                    "2x - y = 3"
                )
            else:
                msg = (
                    "Input Error:\n"
                    "This tool solves systems of two linear equations in x and y only.\n"
                    "Your input contains non-linear expressions.\n"
                    "Please enter valid equations such as:\n"
                    "x + y = 4\n"
                    "2x - y = 3"
                )
            return {'error': msg}
        
        steps = [f"System: ${latex(eq1)}$ , ${latex(eq2)}$"]
        
        # Solve with dict output
        sol = solve((eq1_std, eq2_std), syms, dict=True)
        
        steps.append(f"{t['solve']} using substitution/elimination:")
        
        result_latex = ""
        if isinstance(sol, list):
            if len(sol) == 0:
                steps.append("No solution (Parallel lines)")
                result_latex = "\\phi"
            elif len(sol) == 1 and isinstance(sol[0], dict):
                sol_str = ", ".join([f"{latex(k)} = {latex(v)}" for k,v in sol[0].items()])
                steps.append(f"Result: ${sol_str}$")
                result_latex = f"\\{{{sol_str}\\}}"
            else:
                steps.append("Infinite solutions (Coincident lines)")
                result_latex = "Infinite Solutions"
        else:
            # Fallback formatting
            steps.append("Result computed")
            try:
                sol_dict = dict(sol)
                sol_str = ", ".join([f"{latex(k)} = {latex(v)}" for k,v in sol_dict.items()])
                result_latex = f"\\{{{sol_str}\\}}"
            except Exception:
                result_latex = "Solution"
        
        # Plot Data Generation
        plot_data = []
        if len(syms) == 2:
            x, y = syms[0], syms[1]
            lines = [eq1_std, eq2_std]
            colors = ['#4f46e5', '#ec4899']
            
            for i, line_eq in enumerate(lines):
                try:
                    # Try to solve for y
                    y_expr = solve(line_eq, y)
                    if y_expr:
                        y_expr = y_expr[0]
                        # Generate points
                        center_x = 0
                        if isinstance(sol, list) and len(sol) > 0 and x in sol[0]:
                            try: center_x = float(sol[0][x])
                            except: pass
                        
                        x_vals = [center_x - 10, center_x + 10]
                        points = []
                        for val in x_vals:
                            try:
                                y_val = y_expr.subs(x, val)
                                points.append({'x': float(val), 'y': float(y_val)})
                            except: pass
                        
                        if len(points) == 2:
                            plot_data.append({
                                'label': f"Eq {i+1}",
                                'points': points,
                                'color': colors[i],
                                'type': 'line'
                            })
                    else:
                        # Maybe vertical line x = c
                        x_expr = solve(line_eq, x)
                        if x_expr:
                            val = float(x_expr[0])
                            points = [{'x': val, 'y': -10}, {'x': val, 'y': 10}]
                            plot_data.append({
                                'label': f"Eq {i+1}",
                                'points': points,
                                'color': colors[i],
                                'type': 'line'
                            })
                except Exception as e:
                    pass

            # Intersection point
            if isinstance(sol, list) and len(sol) == 1:
                sol_dict = sol[0]
                try:
                    pt = {'x': float(sol_dict[x]), 'y': float(sol_dict[y])}
                    plot_data.append({
                        'label': 'Intersection' if lang == 'en' else 'نقطة التقاطع',
                        'points': [pt],
                        'type': 'point',
                        'color': '#10b981'
                    })
                except: pass
             
        return {'latex': result_latex, 'steps': steps, 'plot_data': plot_data}
    except Exception as e:
        return {'error': str(e)}

def find_polynomial_zeros(poly_str, lang='en'):
    phrases = {
        'en': {
            'function': 'Function',
            'set_zero': 'Set f(x) = 0',
            'factorize': 'Factorize',
            'zeros': 'Zeros',
        },
        'ar': {
            'function': 'الدالة',
            'set_zero': 'بوضع د(س) = 0',
            'factorize': 'التحليل',
            'zeros': 'الأصفار',
        }
    }
    t = phrases.get(lang, phrases['en'])
    try:
        poly = safe_sympify(poly_str)
        zeros = solve(poly)
        steps = [f"{t['function']}: $f(x) = {latex(poly)}$", f"{t['set_zero']}: ${latex(Eq(poly, 0))}$"]
        
        # Factorize if possible
        factored = factor(poly)
        if factored != poly:
            steps.append(f"{t['factorize']}: ${latex(Eq(factored, 0))}$")
            
        zeros_latex = ', '.join([latex(z) for z in zeros])
        steps.append(f"{t['zeros']}: ${zeros_latex}$")
        return {'latex': zeros_latex, 'steps': steps}
    except Exception as e:
        return {'error': str(e)}

def solve_mixed_system_steps(linear_str, quad_str, lang='en'):
    phrases = {
        'en': {
            'system': 'System',
            'linear': 'Linear',
            'quadratic': 'Quadratic',
            'solve_sub': 'Solve linear equation for one variable and substitute into quadratic.',
            'solutions': 'Solutions',
        },
        'ar': {
            'system': 'النظام',
            'linear': 'خطية',
            'quadratic': 'تربيعية',
            'solve_sub': 'حل المعادلة الخطية لمتغير واحد والتعويض في المعادلة التربيعية.',
            'solutions': 'الحلول',
        }
    }
    t = phrases.get(lang, phrases['en'])
    try:
        linear = to_eq(linear_str)
        quad = to_eq(quad_str)
        
        l_std = linear.lhs - linear.rhs
        q_std = quad.lhs - quad.rhs
        
        syms = list(l_std.free_symbols.union(q_std.free_symbols))
        syms.sort(key=lambda s: str(s))
        
        steps = [f"{t['system']}: ${latex(linear)}$ ({t['linear']})", f"${latex(quad)}$ ({t['quadratic']})"]
        
        # Use dict=True for consistent solution format
        solutions = solve((l_std, q_std), syms, dict=True)
        
        steps.append(t['solve_sub'])
        
        sol_strs = []
        if not solutions:
            no_sol = "No real solutions" if lang == 'en' else "لا توجد حلول حقيقية"
            sol_strs.append(no_sol)
        else:
            for s in solutions:
                if isinstance(s, dict):
                     parts = [f"{latex(sym)} = {latex(val)}" for sym, val in s.items()]
                     sol_strs.append("(" + ", ".join(parts) + ")")
        
        steps.append(f"{t['solutions']}: ${', '.join(sol_strs)}$")
        
        result_latex = f"\\{{{', '.join(sol_strs)}\\}}" if solutions else "\\phi"
        return {'latex': result_latex, 'steps': steps}
    except Exception as e:
        return {'error': str(e)}

def simplify_algebraic_fraction(frac_str, lang='en'):
    phrases = {
        'en': {
            'original': 'Original',
            'factor_numer': 'Factor Numerator',
            'factor_denom': 'Factor Denominator',
            'domain': 'Domain',
            'simplified': 'Simplified',
        },
        'ar': {
            'original': 'الكسر الأصلي',
            'factor_numer': 'تحليل البسط',
            'factor_denom': 'تحليل المقام',
            'domain': 'المجال',
            'simplified': 'الكسر في أبسط صورة',
        }
    }
    t = phrases.get(lang, phrases['en'])
    try:
        expr = safe_sympify(frac_str)
        numer, denom = expr.as_numer_denom()
        
        steps = [f"{t['original']}: $\\frac{{{latex(numer)}}}{{{latex(denom)}}}$"]
        
        # Factor both
        numer_factored = factor(numer)
        denom_factored = factor(denom)
        
        steps.append(f"{t['factor_numer']}: ${latex(numer_factored)}$")
        steps.append(f"{t['factor_denom']}: ${latex(denom_factored)}$")
        
        # Domain (zeros of denom)
        domain_zeros = solve(denom, dict=False) # list of values
        domain_latex = ", ".join([latex(z) for z in domain_zeros])
        steps.append(f"{t['domain']}: $\\mathbb{{R}} - \\{{{domain_latex}\\}}$")
        
        # Simplify
        simplified = simplify(expr)
        steps.append(f"{t['simplified']}: ${latex(simplified)}$")
        
        return {'latex': latex(simplified), 'steps': steps}
    except Exception as e:
        return {'error': str(e)}

def operate_algebraic_fractions(frac1_str, frac2_str, op, lang='en'):
    phrases = {
        'en': {
            'operation': 'Operation',
            'factor_denoms': 'Factor Denominators',
            'common_domain': 'Common Domain',
            'domain_div': 'Domain (Division)',
            'result_simp': 'Result (Simplified)',
        },
        'ar': {
            'operation': 'العملية',
            'factor_denoms': 'تحليل المقامات',
            'common_domain': 'المجال المشترك',
            'domain_div': 'المجال (في حالة القسمة)',
            'result_simp': 'الناتج في أبسط صورة',
        }
    }
    t = phrases.get(lang, phrases['en'])
    try:
        f1 = safe_sympify(frac1_str)
        f2 = safe_sympify(frac2_str)
        
        steps = [f"{t['operation']}: ${latex(f1)} {op} {latex(f2)}$"]
        
        # 1. Factor denominators to find common denom
        n1, d1 = f1.as_numer_denom()
        n2, d2 = f2.as_numer_denom()
        
        d1_f = factor(d1)
        d2_f = factor(d2)
        
        steps.append(f"{t['factor_denoms']}: $d_1 = {latex(d1_f)}$, $d_2 = {latex(d2_f)}$")
        
        # Domain: Union of zeros of denominators
        zeros1 = solve(d1)
        zeros2 = solve(d2)
        all_zeros = list(set(zeros1 + zeros2))
        domain_latex = ", ".join([latex(z) for z in all_zeros])
        steps.append(f"{t['common_domain']}: $\\mathbb{{R}} - \\{{{domain_latex}\\}}$")
        
        result = None
        if op == '+': result = f1 + f2
        elif op == '-': result = f1 - f2
        elif op == '*': result = f1 * f2
        elif op == '/': 
            # For division, exclude zeros of numerator of divisor too!
            n2_zeros = solve(n2)
            all_zeros += n2_zeros
            domain_latex_div = ", ".join([latex(z) for z in set(all_zeros)])
            steps.append(f"{t['domain_div']}: $\\mathbb{{R}} - \\{{{domain_latex_div}\\}}$")
            result = f1 / f2
            
        result_simp = simplify(result)
        steps.append(f"{t['result_simp']}: ${latex(result_simp)}$")
        
        return {'latex': latex(result_simp), 'steps': steps}
    except Exception as e:
        return {'error': str(e)}

def find_fraction_inverse(frac_str, inv_type='mul', lang='en'):
    phrases = {
        'en': {
            'original': 'Original',
            'mul_inv': 'Multiplicative Inverse: Flip numerator and denominator.',
            'add_inv': 'Additive Inverse: Multiply by -1.',
            'domain': 'Domain',
            'domain_mul_note': '(Zeros of both numerator and denominator)',
            'domain_add_note': '(Same as original)',
            'result': 'Result',
        },
        'ar': {
            'original': 'الكسر الأصلي',
            'mul_inv': 'المعكوس الضربي: قلب البسط والمقام.',
            'add_inv': 'المعكوس الجمعي: الضرب في -1.',
            'domain': 'المجال',
            'domain_mul_note': '(أصفار كل من البسط والمقام)',
            'domain_add_note': '(نفس مجال الكسر الأصلي)',
            'result': 'الناتج',
        }
    }
    t = phrases.get(lang, phrases['en'])
    try:
        expr = safe_sympify(frac_str)
        numer, denom = expr.as_numer_denom()
        
        steps = [f"{t['original']}: $\\frac{{{latex(numer)}}}{{{latex(denom)}}}$"]
        
        # Domain 1 (Original)
        zeros_denom = solve(denom)
        
        result = None
        domain_latex = ""
        
        if inv_type == 'mul':
            # Multiplicative Inverse
            steps.append(t['mul_inv'])
            result = denom / numer
            # New Domain: Exclude zeros of OLD numerator too (which is now denominator)
            zeros_numer = solve(numer)
            all_zeros = list(set(zeros_denom + zeros_numer))
            domain_latex = ", ".join([latex(z) for z in all_zeros])
            steps.append(f"{t['domain']}: $\\mathbb{{R}} - \\{{{domain_latex}\\}}$ {t['domain_mul_note']}")
            
        else:
            # Additive Inverse
            steps.append(t['add_inv'])
            result = -expr
            domain_latex = ", ".join([latex(z) for z in zeros_denom])
            steps.append(f"{t['domain']}: $\\mathbb{{R}} - \\{{{domain_latex}\\}}$ {t['domain_add_note']}")
            
        steps.append(f"{t['result']}: ${latex(result)}$")
        return {'latex': latex(result), 'steps': steps}
    except Exception as e:
        return {'error': str(e)}

def stratified_sample(total, stratum, sample_size):
    # n_i = (N_i / N) * n
    try:
        total = float(total)
        stratum = float(stratum)
        sample_size = float(sample_size)
        
        if total == 0: return {'error': 'Total population cannot be zero'}
        
        result = (stratum / total) * sample_size
        steps = [
            f"Stratum Size ($N_i$): {stratum}",
            f"Total Population ($N$): {total}",
            f"Sample Size ($n$): {sample_size}",
            f"Formula: $n_i = \\frac{{N_i}}{{N}} \\times n$",
            f"Calc: $\\frac{{{stratum}}}{{{total}}} \\times {sample_size} = {result}$",
            f"Result: {round(result)} (approx)"
        ]
        return {'result': round(result), 'steps': steps}
    except Exception as e:
        return {'error': str(e)}

def probability_laws(pa, pb, p_intersect, lang='en'):
    # Returns Union, Diff A-B, Diff B-A, Complement A, Complement B
    try:
        pa = float(pa)
        pb = float(pb)
        p_int = float(p_intersect)
        
        p_union = pa + pb - p_int
        p_diff_a_b = pa - p_int
        p_diff_b_a = pb - p_int
        p_comp_a = 1 - pa
        p_comp_b = 1 - pb
        
        steps = [
            f"$P(A) = {pa}, P(B) = {pb}, P(A \\cap B) = {p_int}$",
            f"1. Union $P(A \\cup B) = P(A) + P(B) - P(A \\cap B) = {pa} + {pb} - {p_int} = {round(p_union, 4)}$",
            f"2. Diff $P(A - B) = P(A) - P(A \\cap B) = {pa} - {p_int} = {round(p_diff_a_b, 4)}$",
            f"3. Diff $P(B - A) = P(B) - P(A \\cap B) = {pb} - {p_int} = {round(p_diff_b_a, 4)}$",
            f"4. Comp $P(A') = 1 - P(A) = 1 - {pa} = {round(p_comp_a, 4)}$"
        ]
        
        return {
            'union': round(p_union, 4),
            'diff_ab': round(p_diff_a_b, 4),
            'comp_a': round(p_comp_a, 4),
            'steps': steps
        }
    except Exception as e:
        return {'error': str(e)}

def solve_circle_angles(angle_type, value, lang='en'):
    phrases = {
        'en': {
            'given_central': 'Given Central Angle',
            'given_inscribed': 'Given Inscribed Angle',
            'given_tangent': 'Given Tangent-Chord Angle',
            'central': 'Central Angle',
            'inscribed': 'Inscribed Angle',
            'tangent': 'Tangent-Chord Angle',
            'formula_inscribed': 'Inscribed Angle = 1/2 * Central',
            'formula_tangent': 'Tangent-Chord Angle = 1/2 * Central',
            'formula_central_from_inscribed': 'Central Angle = 2 * Inscribed',
            'formula_central_from_tangent': 'Central Angle = 2 * Tangent',
            'tangent_equal_inscribed': 'Tangent-Chord Angle = Inscribed Angle'
        },
        'ar': {
            'given_central': 'الزاوية المركزية المعطاة',
            'given_inscribed': 'الزاوية المحيطية المعطاة',
            'given_tangent': 'الزاوية المماسية المعطاة',
            'central': 'الزاوية المركزية',
            'inscribed': 'الزاوية المحيطية',
            'tangent': 'الزاوية المماسية',
            'formula_inscribed': 'الزاوية المحيطية = 1/2 × المركزية',
            'formula_tangent': 'الزاوية المماسية = 1/2 × المركزية',
            'formula_central_from_inscribed': 'الزاوية المركزية = 2 × المحيطية',
            'formula_central_from_tangent': 'الزاوية المركزية = 2 × المماسية',
            'tangent_equal_inscribed': 'الزاوية المماسية = الزاوية المحيطية'
        }
    }
    t = phrases.get(lang, phrases['en'])
    
    try:
        val = float(value)
        steps = []
        
        central = 0
        inscribed = 0
        tangent = 0 # Angle between tangent and chord
        
        if angle_type == 'central':
            central = val
            steps.append(f"{t['given_central']} = ${val}^\\circ$")
            inscribed = val / 2
            tangent = val / 2
            steps.append(f"{t['inscribed']} = $\\frac{{1}}{{2}} \\times \\text{{{t['central']}}} = \\frac{{{val}}}{{2}} = {inscribed}^\\circ$")
            steps.append(f"{t['tangent']} = $\\frac{{1}}{{2}} \\times \\text{{{t['central']}}} = {tangent}^\\circ$")
            
        elif angle_type == 'inscribed':
            inscribed = val
            steps.append(f"{t['given_inscribed']} = ${val}^\\circ$")
            central = val * 2
            tangent = val
            steps.append(f"{t['central']} = $2 \\times \\text{{{t['inscribed']}}} = 2 \\times {val} = {central}^\\circ$")
            steps.append(f"{t['tangent']} = {t['inscribed']} = ${tangent}^\\circ$")
            
        elif angle_type == 'tangent':
            tangent = val
            steps.append(f"{t['given_tangent']} = ${val}^\\circ$")
            central = val * 2
            inscribed = val
            steps.append(f"{t['central']} = $2 \\times \\text{{{t['tangent']}}} = 2 \\times {val} = {central}^\\circ$")
            steps.append(f"{t['inscribed']} = {t['tangent']} = ${inscribed}^\\circ$")
            
        return {
            'central': central,
            'inscribed': inscribed,
            'tangent': tangent,
            'steps': steps
        }
    except Exception as e:
        return {'error': str(e)}

def circle_tangent_calc(r, dist, lang='en'):
    phrases = {
        'en': {
            'radius': 'Radius',
            'distance': 'Distance',
            'outside_error': 'Point must be outside circle (d > r) for tangents.',
            'tangent_length': 'Tangent Length',
            'calc': 'Calc',
            'angle_between': 'Angle between tangents',
        },
        'ar': {
            'radius': 'نصف القطر',
            'distance': 'المسافة',
            'outside_error': 'يجب أن تكون النقطة خارج الدائرة (d > r) لحساب المماسات.',
            'tangent_length': 'طول المماس',
            'calc': 'الحساب',
            'angle_between': 'الزاوية بين المماسين',
        }
    }
    t = phrases.get(lang, phrases['en'])
    try:
        r = float(r)
        d = float(dist)
        
        steps = [f"{t['radius']} ($r$) = {r}", f"{t['distance']} ($d$) = {d}"]
        
        if d <= r:
            return {'error': t['outside_error'], 'steps': steps}
            
        # Tangent Length
        t_len = math.sqrt(d**2 - r**2)
        steps.append(f"{t['tangent_length']}: $t = \\sqrt{{d^2 - r^2}}$")
        steps.append(f"{t['calc']}: $\\sqrt{{{d}^2 - {r}^2}} = \\sqrt{{{d**2} - {r**2}}} = \\sqrt{{{d**2 - r**2}}} = {round(t_len, 2)}$")
        
        # Angle between tangents
        import math as m
        theta_rad = 2 * m.asin(r/d)
        theta_deg = m.degrees(theta_rad)
        
        steps.append(f"{t['angle_between']} ($\\theta$):")
        steps.append(f"$\\sin(\\theta/2) = \\frac{{r}}{{d}} = \\frac{{{r}}}{{{d}}} = {round(r/d, 4)}$")
        steps.append(f"$\\theta = 2 \\times \\arcsin({round(r/d, 4)}) = {round(theta_deg, 2)}^\\circ$")
        
        return {'length': t_len, 'angle': theta_deg, 'steps': steps}
    except Exception as e:
        return {'error': str(e)}

def circle_position_analyzer(r, dist, lang='en'):
    phrases = {
        'en': {
            'radius': 'Radius',
            'distance': 'Distance',
            'outside': 'Outside',
            'on_circle': 'On Circle / Tangent',
            'inside': 'Inside / Secant',
            'center': 'Center',
            'since': 'Since',
        },
        'ar': {
            'radius': 'نصف القطر',
            'distance': 'المسافة',
            'outside': 'خارج الدائرة',
            'on_circle': 'على الدائرة / مماس',
            'inside': 'داخل الدائرة / قاطع',
            'center': 'المركز',
            'since': 'بما أن',
        }
    }
    t = phrases.get(lang, phrases['en'])
    try:
        r = float(r)
        d = float(dist)
        
        pos = ""
        steps = [f"{t['radius']} ($r$) = {r}", f"{t['distance']} ($d$) = {d}"]
        
        if d > r:
            pos = t['outside']
            steps.append(f"{t['since']} $d > r$ ({d} > {r}) -> {t['outside']}.")
        elif d == r:
            pos = t['on_circle']
            steps.append(f"{t['since']} $d = r$ ({d} = {r}) -> {t['on_circle']}.")
        elif d < r and d > 0:
            pos = t['inside']
            steps.append(f"{t['since']} $0 < d < r$ ({d} < {r}) -> {t['inside']}.")
        elif d == 0:
            pos = t['center']
            steps.append(f"{t['since']} $d = 0$ -> {t['center']}.")
            
        return {'position': pos, 'steps': steps}
    except Exception as e:
        return {'error': str(e)}

def cyclic_quad_check(angle_opp_1, angle_opp_2, lang='en'):
    phrases = {
        'en': {
            'angle1': 'Angle 1',
            'angle2': 'Angle 2 (Opposite)',
            'sum': 'Sum',
            'cyclic': 'Cyclic Quadrilateral',
            'not_cyclic': 'Not Cyclic Quadrilateral',
            'since_sum': 'Since Sum',
        },
        'ar': {
            'angle1': 'الزاوية 1',
            'angle2': 'الزاوية 2 (المقابلة)',
            'sum': 'المجموع',
            'cyclic': 'رباعي دائري',
            'not_cyclic': 'ليس رباعي دائري',
            'since_sum': 'بما أن المجموع',
        }
    }
    t = phrases.get(lang, phrases['en'])
    try:
        a1 = float(angle_opp_1)
        a2 = float(angle_opp_2)
        total = a1 + a2
        
        is_cyclic = abs(total - 180) < 0.001
        steps = [
            f"{t['angle1']} = {a1}, {t['angle2']} = {a2}",
            f"{t['sum']} = {a1} + {a2} = {total}"
        ]
        
        if is_cyclic:
            steps.append(f"{t['since_sum']} = 180 -> {t['cyclic']}")
        else:
            steps.append(f"{t['since_sum']} {total} != 180 -> {t['not_cyclic']}")
            
        return {'is_cyclic': is_cyclic, 'steps': steps}
    except Exception as e:
        return {'error': str(e)}

def sexagesimal_convert(val, to_type='deg', lang='en'):
    phrases = {
        'en': {
            'input': 'Input',
            'formula': 'Formula',
            'calc': 'Calc',
            'degrees': 'Degrees',
            'minutes': 'Minutes',
            'seconds': 'Seconds',
        },
        'ar': {
            'input': 'المدخل',
            'formula': 'القانون',
            'calc': 'الحساب',
            'degrees': 'الدرجات',
            'minutes': 'الدقائق',
            'seconds': 'الثواني',
        }
    }
    t = phrases.get(lang, phrases['en'])
    # to_type='deg' (DMS to Decimal), 'dms' (Decimal to DMS)
    try:
        steps = []
        result = None
        
        if to_type == 'deg':
            # Input format expected: "D M S" or separate args. Simplified: val is dict or string "D.M.S"
            # Assuming val is string "D M S" space separated
            parts = list(map(float, val.strip().split()))
            d = parts[0]
            m = parts[1] if len(parts) > 1 else 0
            s = parts[2] if len(parts) > 2 else 0
            
            steps.append(f"{t['input']}: {d}° {m}' {s}''")
            decimal = d + (m/60.0) + (s/3600.0)
            steps.append(f"{t['formula']}: $D + \\frac{{M}}{{60}} + \\frac{{S}}{{3600}}$")
            steps.append(f"{t['calc']}: ${d} + \\frac{{{m}}}{{60}} + \\frac{{{s}}}{{3600}} = {decimal}$")
            result = decimal
            
        else: # to_dms
            deg_dec = float(val)
            steps.append(f"{t['input']}: {deg_dec}°")
            
            d = int(deg_dec)
            rem = (deg_dec - d) * 60
            m = int(rem)
            s = (rem - m) * 60
            
            steps.append(f"{t['degrees']}: {d}")
            steps.append(f"{t['minutes']}: $({deg_dec} - {d}) \\times 60 = {rem} \\rightarrow {m}$")
            steps.append(f"{t['seconds']}: $({rem} - {m}) \\times 60 = {s}$")
            
            result = f"{d}° {m}' {round(s, 2)}''"
            
        return {'result': result, 'steps': steps}
    except Exception as e:
        return {'error': str(e)}

def midpoint_slope_calc(x1, y1, x2, y2, calc_type='midpoint', lang='en'):
    phrases = {
        'en': {
            'points': 'Points',
            'formula_mid': 'Formula (Midpoint)',
            'formula_slope': 'Formula (Slope)',
            'calc': 'Calc',
            'undefined': 'Undefined (Vertical Line)',
            'div_zero': 'Division by zero',
        },
        'ar': {
            'points': 'النقاط',
            'formula_mid': 'القانون (نقطة المنتصف)',
            'formula_slope': 'القانون (الميل)',
            'calc': 'الحساب',
            'undefined': 'غير معرف (خط رأسي)',
            'div_zero': 'القسمة على صفر',
        }
    }
    t = phrases.get(lang, phrases['en'])
    try:
        x1, y1, x2, y2 = map(float, [x1, y1, x2, y2])
        steps = [f"{t['points']}: $A({x1}, {y1})$, $B({x2}, {y2})$"]
        
        if calc_type == 'midpoint':
            xm = (x1 + x2) / 2
            ym = (y1 + y2) / 2
            steps.append(f"{t['formula_mid']}: $M = (\\frac{{x_1+x_2}}{{2}}, \\frac{{y_1+y_2}}{{2}})$")
            steps.append(f"{t['calc']}: $(\\frac{{{x1}+{x2}}}{{2}}, \\frac{{{y1}+{y2}}}{{2}}) = ({xm}, {ym})$")
            return {'result': f"({xm}, {ym})", 'steps': steps}
            
        elif calc_type == 'slope':
            if x2 - x1 == 0:
                return {'result': t['undefined'], 'steps': steps + [t['div_zero']]}
            m = (y2 - y1) / (x2 - x1)
            steps.append(f"{t['formula_slope']}: $m = \\frac{{y_2-y_1}}{{x_2-x_1}}$")
            steps.append(f"{t['calc']}: $\\frac{{{y2}-{y1}}}{{{x2}-{x1}}} = {m}$")
            return {'result': m, 'steps': steps}
            
    except Exception as e:
        return {'error': str(e)}
