from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.http import Http404, JsonResponse
from django.core.cache import cache
import hashlib
import json
from .models import Tool, GradeTool
from grades.models import Grade
from .engine import (
    calculate_expression, solve_equation_step_by_step, expand_algebraic_expression, 
    polynomial_long_division_steps, simplify_exponents_steps, convert_scientific_notation, 
    factorize_expression_steps, quadrilateral_area, pythagoras_converse, probability_simulator,
    solve_linear_system_steps, solve_mixed_system_steps, find_polynomial_zeros, 
    simplify_algebraic_fraction, operate_algebraic_fractions, find_fraction_inverse,
    stratified_sample, probability_laws, circle_position_analyzer, cyclic_quad_check,
    sexagesimal_convert, midpoint_slope_calc, circle_tangent_calc, solve_circle_angles
)

def get_cache_key(prefix, data, lang):
    """Generate a unique cache key based on input data and language."""
    try:
        # Sort keys to ensure consistent JSON string
        data_str = json.dumps(data, sort_keys=True)
        key_hash = hashlib.md5(f"{data_str}:{lang}".encode('utf-8')).hexdigest()
        return f"{prefix}:{key_hash}"
    except Exception:
        return None

class ToolView(View):
    def get(self, request, tool_slug):
        # Ensure grade is selected
        grade_id = request.session.get('grade_id')
        if not grade_id:
            return redirect('core:home')
            
        grade = get_object_or_404(Grade, id=grade_id)
        tool = get_object_or_404(Tool, slug=tool_slug)
        
        # Check if tool is allowed for this grade
        try:
            grade_tool_config = GradeTool.objects.get(grade=grade, tool=tool, is_active=True)
        except GradeTool.DoesNotExist:
            raise Http404("Tool not available for this grade")

        context = {
            'tool': tool,
            'grade': grade,
            'config': grade_tool_config.config_json
        }
        
        # Route to specific template based on tool type
        if tool.tool_type == 'CALC':
            return render(request, 'tools/calculator.html', context)
        elif tool.tool_type == 'SOLVER':
            return render(request, 'tools/solver.html', context)
        elif tool.tool_type == 'GEO':
            return render(request, 'tools/geometry.html', context)
        elif tool.tool_type == 'GRAPH': # Added Graph Support
            return render(request, 'tools/graph.html', context)
        elif tool.tool_type == 'UNIT':
            return render(request, 'tools/unit_converter.html', context)
        elif tool.tool_type == 'MATRIX':
            return render(request, 'tools/matrix.html', context)
        elif tool.tool_type == 'PROB':
            return render(request, 'tools/probability.html', context)
        else:
            return render(request, 'tools/generic_tool.html', context)

class CalculatorAPI(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            expression = data.get('expression')
            
            # Get grade config
            grade_id = request.session.get('grade_id')
            config = {}
            if grade_id:
                # In a real app, cache this lookup
                # For MVP, we'll try to find the Calc tool config for this grade
                pass 

            lang = request.session.get('lang', 'en')
            
            # Check cache
            cache_key = get_cache_key('calc', data, lang)
            if cache_key:
                cached_result = cache.get(cache_key)
                if cached_result:
                    return JsonResponse(cached_result)

            result = calculate_expression(expression, config=config, lang=lang)
            
            # Set cache (24 hours)
            if cache_key:
                cache.set(cache_key, result, timeout=86400)
                
            return JsonResponse(result)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class GeometryAPI(View):
    def get(self, request):
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    def post(self, request):
        try:
            if not request.body:
                 return JsonResponse({'error': 'Empty request body'}, status=400)
                 
            data = json.loads(request.body)
            mode = data.get('mode')
            lang = request.session.get('lang', 'en')
            
            # Check cache
            cache_key = get_cache_key('geo', data, lang)
            if cache_key:
                cached_result = cache.get(cache_key)
                if cached_result:
                    return JsonResponse(cached_result)
            
            if mode == 'area':
                shape = data.get('shape')
                params = data.get('params')
                result = quadrilateral_area(shape, params, lang=lang)
            elif mode == 'converse':
                a = data.get('a')
                b = data.get('b')
                c = data.get('c')
                result = pythagoras_converse(a, b, c, lang=lang)
            # New Modes for Grade 9
            elif mode == 'circle_pos':
                r = data.get('r')
                dist = data.get('dist')
                result = circle_position_analyzer(r, dist, lang=lang)
            elif mode == 'cyclic_check':
                a1 = data.get('a1')
                a2 = data.get('a2')
                result = cyclic_quad_check(a1, a2, lang=lang)
            elif mode == 'tangent':
                r = data.get('r')
                dist = data.get('dist')
                result = circle_tangent_calc(r, dist, lang=lang)
            elif mode == 'midpoint_slope':
                x1 = data.get('x1')
                y1 = data.get('y1')
                x2 = data.get('x2')
                y2 = data.get('y2')
                ctype = data.get('type', 'midpoint')
                result = midpoint_slope_calc(x1, y1, x2, y2, ctype, lang=lang)
            elif mode == 'sexagesimal':
                val = data.get('value')
                ctype = data.get('type', 'deg')
                result = sexagesimal_convert(val, ctype, lang=lang)
            elif mode == 'circle_angles':
                atype = data.get('type')
                val = data.get('value')
                result = solve_circle_angles(atype, val, lang=lang)
            else:
                return JsonResponse({'error': 'Invalid mode'}, status=400)
                
            # Set cache (24 hours)
            if cache_key:
                cache.set(cache_key, result, timeout=86400)

            return JsonResponse(result)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class ProbabilityAPI(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            sim_type = data.get('type')
            lang = request.session.get('lang', 'en')
            
            # Probability simulations (coin, dice, cards) are random, so NO CACHING for them.
            # But stratified sample and laws are deterministic.
            
            if sim_type in ['coin', 'dice', 'cards']:
                trials = data.get('trials', 1)
                result = probability_simulator(sim_type, trials, lang=lang)
            elif sim_type == 'stratified':
                total = data.get('total')
                stratum = data.get('stratum')
                sample = data.get('sample')
                result = stratified_sample(total, stratum, sample)
            elif sim_type == 'laws':
                pa = data.get('pa')
                pb = data.get('pb')
                p_int = data.get('p_int')
                result = probability_laws(pa, pb, p_int, lang=lang)
            else:
                return JsonResponse({'error': 'Invalid type'}, status=400)
                
            return JsonResponse(result)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


class SolverAPI(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            mode = data.get('mode', 'solve') # solve, expand, divide
            lang = request.session.get('lang', 'en')
            
            # Check cache
            cache_key = get_cache_key('solver', data, lang)
            if cache_key:
                cached_result = cache.get(cache_key)
                if cached_result:
                    return JsonResponse(cached_result)

            if mode == 'expand':
                expression = data.get('expression')
                result = expand_algebraic_expression(expression, lang=lang)
            elif mode == 'factorize':
                expression = data.get('expression')
                result = factorize_expression_steps(expression, lang=lang)
            elif mode == 'simplify':
                expression = data.get('expression')
                result = simplify_exponents_steps(expression, lang=lang)
            elif mode == 'scientific':
                value = data.get('value')
                result = convert_scientific_notation(value, lang=lang)
            elif mode == 'divide':
                dividend = data.get('dividend')
                divisor = data.get('divisor')
                result = polynomial_long_division_steps(dividend, divisor, lang=lang)
            # New Modes for Grade 9
            elif mode == 'linear_system':
                eq1 = data.get('eq1')
                eq2 = data.get('eq2')
                result = solve_linear_system_steps(eq1, eq2, lang=lang)
            elif mode == 'mixed_system':
                linear = data.get('linear')
                quad = data.get('quad')
                result = solve_mixed_system_steps(linear, quad, lang=lang)
            elif mode == 'poly_zeros':
                poly = data.get('poly')
                result = find_polynomial_zeros(poly, lang=lang)
            elif mode == 'simplify_fraction':
                frac = data.get('fraction')
                result = simplify_algebraic_fraction(frac, lang=lang)
            elif mode == 'operate_fraction':
                f1 = data.get('f1')
                f2 = data.get('f2')
                op = data.get('op')
                result = operate_algebraic_fractions(f1, f2, op, lang=lang)
            elif mode == 'inverse_fraction':
                frac = data.get('fraction')
                itype = data.get('type', 'mul')
                result = find_fraction_inverse(frac, itype, lang=lang)
            else:
                equation = data.get('equation')
                result = solve_equation_step_by_step(equation, lang=lang)
                
            # Set cache (24 hours)
            if cache_key:
                cache.set(cache_key, result, timeout=86400)
                
            return JsonResponse(result)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
