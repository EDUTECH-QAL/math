
import sys
import os

# Add the current directory to sys.path to import engine
sys.path.append(os.getcwd())

from tools.engine import solve_linear_system_steps, solve_mixed_system_steps

def test_systems():
    print("Testing Linear System...")
    # This should work if to_eq handles =
    res1 = solve_linear_system_steps("x + y = 4", "x - y = 2", lang='ar')
    if 'error' in res1:
        print(f"Linear System Error: {res1['error']}")
    else:
        print(f"Linear System Success: {res1['latex']}")

    print("\nTesting Mixed System...")
    # This is likely where it fails because it uses safe_sympify directly
    res2 = solve_mixed_system_steps("y = x + 1", "y = x**2 - 1", lang='ar')
    if 'error' in res2:
        print(f"Mixed System Error: {res2['error']}")
    else:
        print(f"Mixed System Success: {res2['latex']}")

if __name__ == "__main__":
    test_systems()
