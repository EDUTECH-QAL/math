import sympy
from sympy import symbols, solve, Eq, factor, expand, simplify, latex, Rational, oo, S, sympify, sqrt, Abs, degree
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
import random
import math
import math as m

def sanitize_expression(expr_str):
    """
    Sanitizes the input expression string for SymPy.
    Replaces common non-standard mathematical symbols.
    """
    if not expr_str:
        return ""
    # Replace caret with double asterisk for power
    expr_str = expr_str.replace('^', '**')
    # Replace division symbol
    expr_str = expr_str.replace('÷', '/')
    # Replace multiplication symbol (if used)
    expr_str = expr_str.replace('×', '*')
    return expr_str

def safe_sympify(expr_str):
    """
    Safely parses a math expression string into a SymPy expression.
    Handles ^ for power and implicit multiplication (e.g. 5x).
    Maps 'log' to base 10 log and 'ln' to natural log.
    """
    if not expr_str: return None
    clean_str = sanitize_expression(expr_str)
    transformations = (standard_transformations + (implicit_multiplication_application,))
    
    local_dict = {
        'log': lambda x: sympy.log(x, 10),
        'ln': sympy.log,
        'e': sympy.E,
        'pi': sympy.pi
    }
    
    return parse_expr(clean_str, transformations=transformations, local_dict=local_dict)

def calculate_expression(expression, config={}, lang='en'):
    """
    Evaluates a mathematical expression.
    """
    try:
        err_msg = "Invalid Expression" if lang == 'en' else "تعبير غير صالح"
        if not expression: return {'error': err_msg}
        
        expr = safe_sympify(expression)
        result = expr.evalf()
        return {'result': str(result), 'latex': latex(expr)}
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
        # Handle inequalities briefly (not full support yet)
        if '>' in equation_str or '<' in equation_str:
            # Fallback for now or use solve_univariate_inequality
            pass

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
        
        for s in solutions:
            sol_latex_list.append(latex(s))
            
        sol_latex = ', '.join(sol_latex_list)
        
        # Simple plot data for single real solution
        if len(solutions) == 1 and solutions[0].is_real:
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
        q, r = sympy.div(dividend, divisor)
        steps = [
            f"Divide ${latex(dividend)}$ by ${latex(divisor)}$",
            f"Quotient: ${latex(q)}$",
            f"Remainder: ${latex(r)}$",
            f"Result: ${latex(q)} + \\frac{{{latex(r)}}}{{{latex(divisor)}}}$"
        ]
        return {'latex': latex(q), 'steps': steps}
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

def convert_scientific_notation(value_str, lang='en'):
    try:
        val = float(value_str)
        sci = "{:.2e}".format(val)
        base, exponent = sci.split('e')
        latex_sci = f"{base} \\times 10^{{{int(exponent)}}}"
        return {'latex': latex_sci, 'steps': [f"Value: {val}", f"Scientific: ${latex_sci}$"]}
    except Exception as e:
        return {'error': str(e)}

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
        expr = safe_sympify(expression_str)
        steps = [f"{t['original']}: ${latex(expr)}$"]
        
        # 1. Check for Common Factor
        terms = list(sympy.Add.make_args(expr))
        common = sympy.gcd(terms)
        if common != 1:
            steps.append(f"{t['common_factor']}: {latex(common)}")
            expr = factor(expr)
            steps.append(f"${latex(common)} ({latex(expr/common)})$")
        
        factored = factor(expr)
        
        # Try to guess method based on expression structure
        if expr.is_Add and len(terms) == 2:
            # Check signs
            c1, c2 = terms[0], terms[1]
            if (c1.is_Mul and c1.as_coeff_Mul()[0] < 0) or (c2.is_Mul and c2.as_coeff_Mul()[0] < 0):
                steps.append(f"{t['identify']}: {t['diff_squares']}")
            elif degree(expr) == 3:
                steps.append(f"{t['identify']}: {t['sum_cubes']} / {t['diff_cubes']}")
        elif expr.is_Add and len(terms) == 3:
             if degree(expr) == 2:
                 steps.append(f"{t['identify']}: {t['trinomial']}")
        elif expr.is_Add and len(terms) == 4:
             steps.append(f"{t['identify']}: {t['grouping']}")

        if factored != expr:
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

def solve_linear_system_steps(eq1_str, eq2_str, lang='en'):
    t = {
        'en': {'step': 'Step', 'isolate': 'Isolate', 'sub': 'Substitute', 'solve': 'Solve', 'result': 'Solution'},
        'ar': {'step': 'خطوة', 'isolate': 'عزل', 'sub': 'التعويض', 'solve': 'حل', 'result': 'مجموعة الحل'}
    }.get(lang, {'step': 'Step'})
    
    try:
        # Parsing
        eq1 = safe_sympify(eq1_str)
        eq2 = safe_sympify(eq2_str)
        
        # Ensure equations are Eq objects
        if not isinstance(eq1, Eq): eq1 = Eq(eq1, 0)
        if not isinstance(eq2, Eq): eq2 = Eq(eq2, 0)

        # Standardize: LHS - RHS = 0
        eq1_std = eq1.lhs - eq1.rhs
        eq2_std = eq2.lhs - eq2.rhs
        
        syms = list(eq1_std.free_symbols.union(eq2_std.free_symbols))
        # Default sort x, y
        syms.sort(key=lambda s: str(s))
        if len(syms) == 0: syms = [symbols('x'), symbols('y')]
        
        steps = [f"System: ${latex(eq1)}$ , ${latex(eq2)}$"]
        
        # Solve
        sol = solve((eq1_std, eq2_std), syms)
        
        steps.append(f"{t['solve']} using substitution/elimination:")
        
        result_latex = ""
        if isinstance(sol, dict):
            # Single solution
            sol_str = ", ".join([f"{latex(k)} = {latex(v)}" for k,v in sol.items()])
            steps.append(f"Result: ${sol_str}$")
            result_latex = f"\\{{{sol_str}\\}}"
        elif isinstance(sol, list):
             # Multiple or no solution
             if len(sol) == 0:
                 steps.append("No solution (Parallel lines)")
                 result_latex = "\\phi"
             else:
                 # Infinite solutions or other
                 steps.append("Infinite solutions (Coincident lines)")
                 result_latex = "Infinite Solutions"
        
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
                        if isinstance(sol, dict) and x in sol:
                            try: center_x = float(sol[x])
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
            if isinstance(sol, dict):
                try:
                    pt = {'x': float(sol[x]), 'y': float(sol[y])}
                    plot_data.append({
                        'label': 'Intersection',
                        'points': [pt],
                        'type': 'point',
                        'color': '#10b981'
                    })
                except: pass
             
        return {'latex': result_latex, 'steps': steps, 'plot_data': plot_data}
    except Exception as e:
        return {'error': str(e)}

def find_polynomial_zeros(poly_str, lang='en'):
    try:
        poly = safe_sympify(poly_str)
        zeros = solve(poly)
        steps = [f"Function: $f(x) = {latex(poly)}$", f"Set $f(x) = 0$: ${latex(Eq(poly, 0))}$"]
        
        # Factorize if possible
        factored = factor(poly)
        if factored != poly:
            steps.append(f"Factorize: ${latex(Eq(factored, 0))}$")
            
        zeros_latex = ', '.join([latex(z) for z in zeros])
        steps.append(f"Zeros: ${zeros_latex}$")
        return {'latex': zeros_latex, 'steps': steps}
    except Exception as e:
        return {'error': str(e)}

def solve_mixed_system_steps(linear_str, quad_str, lang='en'):
    try:
        linear = safe_sympify(linear_str)
        quad = safe_sympify(quad_str)
        
        # Assume linear is eq1, quad is eq2
        if not isinstance(linear, Eq): linear = Eq(linear, 0)
        if not isinstance(quad, Eq): quad = Eq(quad, 0)
        
        l_std = linear.lhs - linear.rhs
        q_std = quad.lhs - quad.rhs
        
        syms = list(l_std.free_symbols.union(q_std.free_symbols))
        syms.sort(key=lambda s: str(s))
        
        steps = [f"System: ${latex(linear)}$ (Linear)", f"${latex(quad)}$ (Quadratic)"]
        
        solutions = solve((l_std, q_std), syms)
        
        steps.append(f"Solve linear equation for one variable and substitute into quadratic.")
        
        sol_strs = []
        for s in solutions:
            if isinstance(s, tuple):
                 parts = [f"{latex(syms[i])} = {latex(val)}" for i, val in enumerate(s)]
                 sol_strs.append("(" + ", ".join(parts) + ")")
            
        steps.append(f"Solutions: ${', '.join(sol_strs)}$")
        
        return {'latex': f"\\{{{', '.join(sol_strs)}\\}}", 'steps': steps}
    except Exception as e:
        return {'error': str(e)}

def simplify_algebraic_fraction(frac_str, lang='en'):
    try:
        expr = safe_sympify(frac_str)
        numer, denom = expr.as_numer_denom()
        
        steps = [f"Original: $\\frac{{{latex(numer)}}}{{{latex(denom)}}}$"]
        
        # Factor both
        numer_factored = factor(numer)
        denom_factored = factor(denom)
        
        steps.append(f"Factor Numerator: ${latex(numer_factored)}$")
        steps.append(f"Factor Denominator: ${latex(denom_factored)}$")
        
        # Domain (zeros of denom)
        domain_zeros = solve(denom, dict=False) # list of values
        domain_latex = ", ".join([latex(z) for z in domain_zeros])
        steps.append(f"Domain: $\\mathbb{{R}} - \\{{{domain_latex}\\}}$")
        
        # Simplify
        simplified = simplify(expr)
        steps.append(f"Simplified: ${latex(simplified)}$")
        
        return {'latex': latex(simplified), 'steps': steps}
    except Exception as e:
        return {'error': str(e)}

def operate_algebraic_fractions(frac1_str, frac2_str, op, lang='en'):
    try:
        f1 = safe_sympify(frac1_str)
        f2 = safe_sympify(frac2_str)
        
        steps = [f"Operation: ${latex(f1)} {op} {latex(f2)}$"]
        
        # 1. Factor denominators to find common denom
        n1, d1 = f1.as_numer_denom()
        n2, d2 = f2.as_numer_denom()
        
        d1_f = factor(d1)
        d2_f = factor(d2)
        
        steps.append(f"Factor Denominators: $d_1 = {latex(d1_f)}$, $d_2 = {latex(d2_f)}$")
        
        # Domain: Union of zeros of denominators
        zeros1 = solve(d1)
        zeros2 = solve(d2)
        all_zeros = list(set(zeros1 + zeros2))
        domain_latex = ", ".join([latex(z) for z in all_zeros])
        steps.append(f"Common Domain: $\\mathbb{{R}} - \\{{{domain_latex}\\}}$")
        
        result = None
        if op == '+': result = f1 + f2
        elif op == '-': result = f1 - f2
        elif op == '*': result = f1 * f2
        elif op == '/': 
            # For division, exclude zeros of numerator of divisor too!
            n2_zeros = solve(n2)
            all_zeros += n2_zeros
            domain_latex_div = ", ".join([latex(z) for z in set(all_zeros)])
            steps.append(f"Domain (Division): $\\mathbb{{R}} - \\{{{domain_latex_div}\\}}$")
            result = f1 / f2
            
        result_simp = simplify(result)
        steps.append(f"Result (Simplified): ${latex(result_simp)}$")
        
        return {'latex': latex(result_simp), 'steps': steps}
    except Exception as e:
        return {'error': str(e)}

def find_fraction_inverse(frac_str, inv_type='mul', lang='en'):
    try:
        expr = safe_sympify(frac_str)
        numer, denom = expr.as_numer_denom()
        
        steps = [f"Original: $\\frac{{{latex(numer)}}}{{{latex(denom)}}}$"]
        
        # Domain 1 (Original)
        zeros_denom = solve(denom)
        
        result = None
        domain_latex = ""
        
        if inv_type == 'mul':
            # Multiplicative Inverse
            steps.append("Multiplicative Inverse: Flip numerator and denominator.")
            result = denom / numer
            # New Domain: Exclude zeros of OLD numerator too (which is now denominator)
            zeros_numer = solve(numer)
            all_zeros = list(set(zeros_denom + zeros_numer))
            domain_latex = ", ".join([latex(z) for z in all_zeros])
            steps.append(f"Domain: $\\mathbb{{R}} - \\{{{domain_latex}\\}}$ (Zeros of both numerator and denominator)")
            
        else:
            # Additive Inverse
            steps.append("Additive Inverse: Multiply by -1.")
            result = -expr
            domain_latex = ", ".join([latex(z) for z in zeros_denom])
            steps.append(f"Domain: $\\mathbb{{R}} - \\{{{domain_latex}\\}}$ (Same as original)")
            
        steps.append(f"Result: ${latex(result)}$")
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
    try:
        val = float(value)
        steps = []
        
        central = 0
        inscribed = 0
        tangent = 0 # Angle between tangent and chord
        
        if angle_type == 'central':
            central = val
            steps.append(f"Given Central Angle = ${val}^\\circ$")
            inscribed = val / 2
            tangent = val / 2
            steps.append(f"Inscribed Angle = $\\frac{{1}}{{2}} \\times \\text{{Central}} = \\frac{{{val}}}{{2}} = {inscribed}^\\circ$")
            steps.append(f"Tangent-Chord Angle = $\\frac{{1}}{{2}} \\times \\text{{Central}} = {tangent}^\\circ$")
            
        elif angle_type == 'inscribed':
            inscribed = val
            steps.append(f"Given Inscribed Angle = ${val}^\\circ$")
            central = val * 2
            tangent = val
            steps.append(f"Central Angle = $2 \\times \\text{{Inscribed}} = 2 \\times {val} = {central}^\\circ$")
            steps.append(f"Tangent-Chord Angle = Inscribed Angle = ${tangent}^\\circ$")
            
        elif angle_type == 'tangent':
            tangent = val
            steps.append(f"Given Tangent-Chord Angle = ${val}^\\circ$")
            central = val * 2
            inscribed = val
            steps.append(f"Central Angle = $2 \\times \\text{{Tangent}} = 2 \\times {val} = {central}^\\circ$")
            steps.append(f"Inscribed Angle = Tangent-Chord Angle = ${inscribed}^\\circ$")
            
        return {
            'central': central,
            'inscribed': inscribed,
            'tangent': tangent,
            'steps': steps
        }
    except Exception as e:
        return {'error': str(e)}

def circle_tangent_calc(r, dist, lang='en'):
    try:
        r = float(r)
        d = float(dist)
        
        steps = [f"Radius ($r$) = {r}", f"Distance ($d$) = {d}"]
        
        if d <= r:
            return {'error': 'Point must be outside circle (d > r) for tangents.', 'steps': steps}
            
        # Tangent Length
        t_len = math.sqrt(d**2 - r**2)
        steps.append(f"Tangent Length: $t = \\sqrt{{d^2 - r^2}}$")
        steps.append(f"Calc: $\\sqrt{{{d}^2 - {r}^2}} = \\sqrt{{{d**2} - {r**2}}} = \\sqrt{{{d**2 - r**2}}} = {round(t_len, 2)}$")
        
        # Angle between tangents
        import math as m
        theta_rad = 2 * m.asin(r/d)
        theta_deg = m.degrees(theta_rad)
        
        steps.append(f"Angle between tangents ($\\theta$):")
        steps.append(f"$\\sin(\\theta/2) = \\frac{{r}}{{d}} = \\frac{{{r}}}{{{d}}} = {round(r/d, 4)}$")
        steps.append(f"$\\theta = 2 \\times \\arcsin({round(r/d, 4)}) = {round(theta_deg, 2)}^\\circ$")
        
        return {'length': t_len, 'angle': theta_deg, 'steps': steps}
    except Exception as e:
        return {'error': str(e)}

def circle_position_analyzer(r, dist, lang='en'):
    try:
        r = float(r)
        d = float(dist)
        
        pos = ""
        steps = [f"Radius ($r$) = {r}", f"Distance ($d$) = {d}"]
        
        if d > r:
            pos = "Outside (خارج الدائرة)"
            steps.append(f"Since $d > r$ ({d} > {r}) -> Point/Line is Outside.")
        elif d == r:
            pos = "On Circle / Tangent (على الدائرة / مماس)"
            steps.append(f"Since $d = r$ ({d} = {r}) -> Point is On Circle / Line is Tangent.")
        elif d < r and d > 0:
            pos = "Inside / Secant (داخل الدائرة / قاطع)"
            steps.append(f"Since $0 < d < r$ ({d} < {r}) -> Point is Inside / Line is Secant.")
        elif d == 0:
            pos = "Center (المركز)"
            steps.append(f"Since $d = 0$ -> Point is the Center.")
            
        return {'position': pos, 'steps': steps}
    except Exception as e:
        return {'error': str(e)}

def cyclic_quad_check(angle_opp_1, angle_opp_2, lang='en'):
    try:
        a1 = float(angle_opp_1)
        a2 = float(angle_opp_2)
        total = a1 + a2
        
        is_cyclic = abs(total - 180) < 0.001
        steps = [
            f"Angle 1 = {a1}, Angle 2 (Opposite) = {a2}",
            f"Sum = {a1} + {a2} = {total}"
        ]
        
        if is_cyclic:
            steps.append("Since Sum = 180 -> Cyclic Quadrilateral (رباعي دائري)")
        else:
            steps.append(f"Since Sum {total} != 180 -> Not Cyclic Quadrilateral (ليس رباعي دائري)")
            
        return {'is_cyclic': is_cyclic, 'steps': steps}
    except Exception as e:
        return {'error': str(e)}

def sexagesimal_convert(val, to_type='deg', lang='en'):
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
            
            steps.append(f"Input: {d}° {m}' {s}''")
            decimal = d + (m/60.0) + (s/3600.0)
            steps.append(f"Formula: $D + \\frac{{M}}{{60}} + \\frac{{S}}{{3600}}$")
            steps.append(f"Calc: ${d} + \\frac{{{m}}}{{60}} + \\frac{{{s}}}{{3600}} = {decimal}$")
            result = decimal
            
        else: # to_dms
            deg_dec = float(val)
            steps.append(f"Input: {deg_dec}°")
            
            d = int(deg_dec)
            rem = (deg_dec - d) * 60
            m = int(rem)
            s = (rem - m) * 60
            
            steps.append(f"Degrees: {d}")
            steps.append(f"Minutes: $({deg_dec} - {d}) \\times 60 = {rem} \\rightarrow {m}$")
            steps.append(f"Seconds: $({rem} - {m}) \\times 60 = {s}$")
            
            result = f"{d}° {m}' {round(s, 2)}''"
            
        return {'result': result, 'steps': steps}
    except Exception as e:
        return {'error': str(e)}

def midpoint_slope_calc(x1, y1, x2, y2, calc_type='midpoint', lang='en'):
    try:
        x1, y1, x2, y2 = map(float, [x1, y1, x2, y2])
        steps = [f"Points: $A({x1}, {y1})$, $B({x2}, {y2})$"]
        
        if calc_type == 'midpoint':
            xm = (x1 + x2) / 2
            ym = (y1 + y2) / 2
            steps.append(f"Formula: $M = (\\frac{{x_1+x_2}}{{2}}, \\frac{{y_1+y_2}}{{2}})$")
            steps.append(f"Calc: $(\\frac{{{x1}+{x2}}}{{2}}, \\frac{{{y1}+{y2}}}{{2}}) = ({xm}, {ym})$")
            return {'result': f"({xm}, {ym})", 'steps': steps}
            
        elif calc_type == 'slope':
            if x2 - x1 == 0:
                return {'result': 'Undefined (Vertical Line)', 'steps': steps + ["Division by zero"]}
            m = (y2 - y1) / (x2 - x1)
            steps.append(f"Formula: $m = \\frac{{y_2-y_1}}{{x_2-x_1}}$")
            steps.append(f"Calc: $\\frac{{{y2}-{y1}}}{{{x2}-{x1}}} = {m}$")
            return {'result': m, 'steps': steps}
            
    except Exception as e:
        return {'error': str(e)}
