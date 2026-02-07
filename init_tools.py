import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from tools.models import Tool, GradeTool
from grades.models import Grade

def init_data():
    print("Initializing Data...")

    # 1. Ensure a Grade exists
    grade, created = Grade.objects.get_or_create(
        slug='general',
        defaults={
            'name_en': 'General Math',
            'name_ar': 'رياضيات عامة',
            'stage': 'SEC',
            'order': 1
        }
    )
    if created:
        print(f"Created Grade: {grade}")
    else:
        print(f"Using Grade: {grade}")

    # 2. Define Tools
    tools_data = [
        {
            'slug': 'calculator',
            'name_en': 'Scientific Calculator',
            'name_ar': 'الآلة الحاسبة العلمية',
            'tool_type': 'CALC',
            'description_en': 'Advanced scientific calculator with history and functions.',
            'description_ar': 'آلة حاسبة علمية متطورة مع سجل وتوابع رياضية.',
            'icon_name': 'fa-calculator'
        },
        {
            'slug': 'solver',
            'name_en': 'Equation Solver',
            'name_ar': 'حلال المعادلات',
            'tool_type': 'SOLVER',
            'description_en': 'Step-by-step solver for linear and quadratic equations.',
            'description_ar': 'حل المعادلات الخطية والتربيعية مع الخطوات التفصيلية.',
            'icon_name': 'fa-wand-magic-sparkles'
        },
        {
            'slug': 'geometry',
            'name_en': 'Geometry Tool',
            'name_ar': 'أدوات الهندسة',
            'tool_type': 'GEO',
            'description_en': 'Calculate area, perimeter, and angles for shapes.',
            'description_ar': 'حساب المساحة والمحيط والزوايا للأشكال الهندسية.',
            'icon_name': 'fa-shapes'
        },
        {
            'slug': 'graph',
            'name_en': 'Graphing Calculator',
            'name_ar': 'الرسم البياني',
            'tool_type': 'GRAPH',
            'description_en': 'Plot multiple functions and analyze their properties.',
            'description_ar': 'رسم دوال متعددة وتحليل خصائصها.',
            'icon_name': 'fa-chart-line'
        },
        {
            'slug': 'unit-converter',
            'name_en': 'Unit Converter',
            'name_ar': 'محول الوحدات',
            'tool_type': 'UNIT',
            'description_en': 'Convert between different units of measurement.',
            'description_ar': 'التحويل بين وحدات القياس المختلفة (طول، وزن، حرارة...).',
            'icon_name': 'fa-ruler-combined'
        },
        {
            'slug': 'matrix',
            'name_en': 'Matrix Calculator',
            'name_ar': 'حاسبة المصفوفات',
            'tool_type': 'MATRIX',
            'description_en': 'Perform matrix operations like addition, multiplication, and inverse.',
            'description_ar': 'العمليات على المصفوفات مثل الجمع والضرب والمعكوس.',
            'icon_name': 'fa-table-cells'
        }
    ]

    for t_data in tools_data:
        tool, created = Tool.objects.update_or_create(
            slug=t_data['slug'],
            defaults={
                'name_en': t_data['name_en'],
                'name_ar': t_data['name_ar'],
                'tool_type': t_data['tool_type'],
                'description_en': t_data['description_en'],
                'description_ar': t_data['description_ar'],
                'icon_name': t_data['icon_name']
            }
        )
        if created:
            print(f"Created Tool: {tool}")
        else:
            print(f"Updated Tool: {tool}")

        # Link to Grade
        gt, gt_created = GradeTool.objects.get_or_create(
            grade=grade,
            tool=tool,
            defaults={'is_active': True}
        )
        if gt_created:
            print(f"Linked {tool} to {grade}")

    print("Initialization Complete.")

if __name__ == '__main__':
    init_data()
