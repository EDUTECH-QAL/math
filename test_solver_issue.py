import sys
import os

# Add current directory to path to import engine
sys.path.append(os.getcwd())

from tools.engine import solve_equation_step_by_step

def test_solver():
    test_cases = [
        ("2x + 4 = 10", "en"),
        ("x^2 - 5x + 6 = 0", "en"),
        ("2^x = 8", "en"),
        ("3^(x+1) = 27", "en"),
        ("x + 1 = x + 2", "en"),
        ("2x = 2x", "en"),
        ("2x + 4 = 10", "ar"),
    ]
    
    for eq, lang in test_cases:
        print(f"Testing ({lang}): {eq}")
        res = solve_equation_step_by_step(eq, lang=lang)
        if 'error' in res:
            print(f"Error: {res['error']}")
        else:
            print(f"Result: {res['latex']}")
            print("Steps:")
            for s in res['steps']:
                print(f"  - {s}")
        print("-" * 20)

if __name__ == "__main__":
    test_solver()
