# Smart Math Tools Platform - System Design & Architecture

## 1. System Architecture (Django Based)

The project follows a modular Django architecture, separating concerns into distinct applications.

### Apps Structure
*   **`config` (Project Root)**: Settings, URL routing, WSGI/ASGI configuration.
*   **`core`**:
    *   **Responsibilities**: Landing page, Global Language management (i18n), Session management for selected Grade/Language.
    *   **Views**: `HomeView`, `SetLanguageView`, `SetGradeView`.
*   **`grades`**:
    *   **Responsibilities**: Managing grade levels (Preparatory, Secondary) and their specific configurations.
    *   **Models**: `Grade`, `Stage`.
*   **`tools`**:
    *   **Responsibilities**: Logic for the mathematical tools.
    *   **Models**: `Tool`, `ToolConfiguration` (links Tool to Grade).
    *   **Components**: Calculator engine, Graphing engine (e.g., using Plotly.js or similar on frontend, logic on backend if needed), Geometry solvers.
*   **`users`** (Phase 3): User authentication, profile, history.

---

## 2. Database Conceptual Design

### ER Diagram Description

#### `grades` App
*   **`Grade`**
    *   `id`: PK
    *   `name_en`: CharField (e.g., "1st Preparatory")
    *   `name_ar`: CharField
    *   `slug`: SlugField (unique)
    *   `stage`: ChoiceField (Preparatory, Secondary)
    *   `order`: IntegerField (for sorting)

#### `tools` App
*   **`Tool`**
    *   `id`: PK
    *   `name_en`: CharField (e.g., "Smart Calculator")
    *   `name_ar`: CharField
    *   `slug`: SlugField (unique)
    *   `type`: ChoiceField (Calculator, Solver, Geometry, Graph)
    *   `description_en`: TextField
    *   `description_ar`: TextField
    *   `icon_name`: CharField (for frontend icon mapping)

*   **`GradeTool`** (Many-to-Many Relationship between Grade and Tool)
    *   `id`: PK
    *   `grade`: FK to `Grade`
    *   `tool`: FK to `Tool`
    *   `is_active`: Boolean
    *   `config_json`: JSONField (Stores grade-specific limitations, e.g., `{"allow_trig": false, "allow_roots": true}`)

---

## 3. Tool Classification per Grade

| Grade Level | Tools Available | Features/Constraints |
| :--- | :--- | :--- |
| **Grade 1 Prep** | Smart Calculator | Basic ops, Fractions, Simple Powers. No Trig. |
| | Equation Solver | Linear equations ($ax + b = c$). |
| | Geometry Tool | Area & Perimeter (Square, Rect, Tri, Circle). |
| **Grade 2 Prep** | *All Grade 1 Tools* | + Roots ($x^2, x^3$). |
| | Graph Tool | Linear functions ($y=mx+c$). |
| | Power Tool | Integer powers. |
| **Secondary** | *All Prep Tools* | + Scientific Mode. |
| | Smart Calculator | Trig ($\sin, \cos, \tan$), Logarithms, Complex numbers. |
| | Quadratic Solver | $ax^2 + bx + c = 0$. |
| | Graphing Functions | Polynomials, Trig functions. |
| | Statistics | Mean, Mode, Median, Standard Deviation. |

---

## 4. User Interface Wireframe Description

### **A. Home Page (Landing)**
*   **Header**: Logo (Left), Language Toggle (Right: EN/AR).
*   **Hero Section**: "Master Math with Smart Tools".
*   **Grade Selection Grid**:
    *   Cards for each stage (Preparatory, Secondary).
    *   Dropdown or buttons for specific grades (e.g., "Grade 1 Prep").
*   **Footer**: Links, Copyright.

### **B. Dashboard (Grade View)**
*   **Context**: "You are in: Grade 1 Prep" (Button to change grade).
*   **Tools Grid**:
    *   Card: **Smart Calculator** (Icon + "Open").
    *   Card: **Equation Solver** (Icon + "Open").
    *   Card: **Geometry** (Icon + "Open").

### **C. Tool Page (e.g., Calculator)**
*   **Sidebar/Top Bar**: Navigation back to Dashboard.
*   **Main Area**:
    *   **Display Screen**: Shows current expression and result. Supports LaTeX rendering (MathJax/KaTeX).
    *   **Keypad**: Dynamic keys based on grade config (e.g., Grade 1 hides $\sin/\cos$).
    *   **History Panel** (Collapsible): Shows previous calculations.
    *   **Steps Panel**: "Show Steps" toggle expands detailed solution below.

---

## 5. Development Phases Plan

### **Phase 1: MVP (Minimum Viable Product)**
*   **Setup**: Django project, Core/Grades/Tools apps.
*   **Data**: Seed data for Grade 1 Prep.
*   **Tools**:
    *   Calculator: Basic + Fractions + History.
    *   Equation Solver: Linear only.
    *   Geometry: Basic 2D shapes.
*   **UI**: Basic Bootstrap/Tailwind layout, Mobile responsive.
*   **Language**: Basic i18n support.

### **Phase 2: Expansion**
*   **Grades**: Add Prep 2, Prep 3, Secondary 1-3.
*   **Tools**:
    *   Graphing Tool implementation (using JS library).
    *   Scientific Calculator features.
*   **Refinement**: Better step-by-step logic.

### **Phase 3: Platform Maturity**
*   **Users App**: Login/Register.
*   **Cloud**: Save history to database.
*   **Analytics**: "Most used tools".
*   **Teacher Mode**: Teachers can suggest toolsets.

---

## 6. Key Features of Smart Calculator

1.  **Adaptive Keypad**:
    *   If `config.allow_trig == false`, hide $\sin, \cos, \tan$ buttons.
2.  **Smart Input Parser**:
    *   Handles `2x` as `2*x`.
    *   Auto-closes parentheses.
3.  **Step-by-Step Engine**:
    *   Not just result ($4$), but logic ($2+2 = 4$).
    *   For equations: Move terms -> Simplify -> Solve.
4.  **Modes**:
    *   **Classic**: Arithmetic.
    *   **Equation**: Solves for $x$.
    *   **Fraction**: Visual fraction input.

---

## 7. UX Flow Explanation

1.  **Entry**: User lands -> Detects Language or Defaults to EN.
2.  **Selection**: User picks "Grade 1 Prep".
3.  **State**: System stores `grade_id=1` in Session/Cookie.
4.  **Discovery**: User sees only relevant tools.
5.  **Action**: User opens "Calculator".
6.  **Task**: User types `2/3 + 1/4`.
7.  **Feedback**: System shows result `11/12` AND steps `(2*4 + 1*3) / 12`.
8.  **Exit/Switch**: User clicks "Dashboard" -> Opens "Geometry" -> Calculates Square Area.

---

## 8. Future Expansion Ideas
*   **OCR / Camera Input**: Take a picture of an equation to solve it.
*   **Voice Input**: "Calculate square root of 144".
*   **Gamification**: Badges for solving X problems.
*   **API**: Public API for other educational apps to use the math engine.
