# System Upgrade Plan: Integrating Smart Math Libraries

## 1. Overview
This upgrade aims to transform the platform from a basic MVP into a robust mathematical engine by integrating **SymPy** (symbolic math), **Plotly** (graphing), **MathJax** (rendering), and standard **Django i18n**.

## 2. Library Integration Strategy

| Feature | Library | Implementation Strategy |
| :--- | :--- | :--- |
| **Smart Calculator** | **SymPy** | Backend processing. Frontend sends expression -> Backend parses/simplifies -> Returns LaTeX & Result. |
| **Equation Solver** | **SymPy** | Backend processing. Solves for variables, returns step-by-step logical breakdown (where possible). |
| **Graph Tool** | **Plotly.js** | Frontend-heavy with backend validation. Backend generates the function data or Plotly JSON layout. |
| **UI Rendering** | **MathJax** | Global script in `base.html`. Auto-renders any element with specific classes (e.g., `.math-tex`). |
| **Localization** | **Django i18n** | Replace custom session logic with `LocaleMiddleware`. Use `.po` files for static text. |

## 3. Architecture Updates

### A. Affected Apps
*   **`config`**: Settings update for i18n and installed apps.
*   **`tools`**:
    *   New Module: `engine.py` (Handles SymPy interactions).
    *   New Views: API endpoints (JSON responses) for tools (`/tools/api/calc/`, `/tools/api/solve/`).
*   **`core`**: Update templates to use `{% trans %}` tags.

### B. Database Changes
*   No major schema changes required for this phase.
*   *Optional*: Add `graph_config` to `GradeTool` JSON to control graph limits per grade.

### C. User Flow Updates
1.  **Calculator/Solver**:
    *   User types `2x + 5 = 15`.
    *   AJAX POST to backend.
    *   Backend (SymPy) solves $x=5$.
    *   Frontend receives JSON: `{ result: "5", steps: ["2x = 10", "x = 5"], latex: "x=5" }`.
    *   MathJax renders the LaTeX.
2.  **Graphing**:
    *   User enters `y = x^2`.
    *   Plotly.js renders interactive chart immediately (or via backend data fetch).

## 4. Implementation Steps
1.  **Install Dependencies**: `sympy`, `plotly`.
2.  **Configure i18n**: Enable middleware, set paths.
3.  **Develop Math Engine**: Create `tools/engine.py` with `calculate()` and `solve_equation()` functions.
4.  **Create API Views**: Django Views that accept JSON and call the Math Engine.
5.  **Frontend Integration**:
    *   Add MathJax to `base.html`.
    *   Rewrite `calculator.html` to use `fetch` and render LaTeX.
    *   Build `solver.html`.
    *   Build `graph.html`.

## 5. Grade-Specific Constraints (Enforced by Engine)
*   **Grade 1 Prep**: Engine rejects trig functions if `config.allow_trig` is False.
*   **Secondary**: Engine allows all SymPy functions.
