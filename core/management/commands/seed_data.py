from django.core.management.base import BaseCommand
from grades.models import Grade
from tools.models import Tool, GradeTool

class Command(BaseCommand):
    help = 'Seeds the database with initial grades and tools'

    def handle(self, *args, **options):
        self.stdout.write('Seeding data...')

        # 1. Create Grades
        grade1_prep, _ = Grade.objects.get_or_create(
            slug='prep-1',
            defaults={
                'name_en': '1st Preparatory',
                'name_ar': 'الاول الاعدادي',
                'stage': 'PREP',
                'order': 1
            }
        )
        
        grade2_prep, _ = Grade.objects.get_or_create(
            slug='prep-2',
            defaults={
                'name_en': '2nd Preparatory',
                'name_ar': 'الثاني الاعدادي',
                'stage': 'PREP',
                'order': 2
            }
        )

        grade3_prep, _ = Grade.objects.get_or_create(
            slug='prep-3',
            defaults={
                'name_en': '3rd Preparatory',
                'name_ar': 'الثالث الاعدادي',
                'stage': 'PREP',
                'order': 3
            }
        )

        # 2. Create Tools
        calc, _ = Tool.objects.get_or_create(
            slug='smart-calculator',
            defaults={
                'name_en': 'Smart Calculator',
                'name_ar': 'الآلة الحاسبة الذكية',
                'tool_type': 'CALC',
                'description_en': 'Advanced calculator with fractions and equations.',
                'description_ar': 'آلة حاسبة متطورة تدعم الكسور والمعادلات.',
                'icon_name': 'fa-calculator'
            }
        )

        solver, _ = Tool.objects.get_or_create(
            slug='equation-solver',
            defaults={
                'name_en': 'Equation Solver',
                'name_ar': 'حل المعادلات',
                'tool_type': 'SOLVER',
                'description_en': 'Solve linear and simple equations step-by-step.',
                'description_ar': 'حل المعادلات الخطية والبسيطة خطوة بخطوة.',
                'icon_name': 'fa-equals'
            }
        )

        geometry, _ = Tool.objects.get_or_create(
            slug='geometry-tool',
            defaults={
                'name_en': 'Geometry Tool',
                'name_ar': 'أدوات الهندسة',
                'tool_type': 'GEO',
                'description_en': 'Calculate Area and Perimeter for shapes.',
                'description_ar': 'حساب المساحة والمحيط للأشكال الهندسية.',
                'icon_name': 'fa-shapes'
            }
        )

        graph, _ = Tool.objects.get_or_create(
            slug='graph-tool',
            defaults={
                'name_en': 'Graph Tool',
                'name_ar': 'الرسم البياني',
                'tool_type': 'GRAPH',
                'description_en': 'Plot linear and quadratic functions.',
                'description_ar': 'رسم الدوال الخطية والتربيعية.',
                'icon_name': 'fa-chart-line'
            }
        )

        # 3. Assign Tools to Grades (Configuration)
        
        # Grade 1 Prep Config
        GradeTool.objects.get_or_create(
            grade=grade1_prep,
            tool=calc,
            defaults={
                'config_json': {
                    'allow_trig': False, 
                    'allow_roots': False,
                    'allow_fractions': True
                }
            }
        )
        GradeTool.objects.get_or_create(
            grade=grade1_prep,
            tool=solver,
            defaults={'config_json': {'max_degree': 1}} # Linear only
        )
        GradeTool.objects.get_or_create(grade=grade1_prep, tool=geometry)

        # Grade 2 Prep Config
        GradeTool.objects.get_or_create(
            grade=grade2_prep,
            tool=calc,
            defaults={
                'config_json': {
                    'allow_trig': False, 
                    'allow_roots': True, # Added roots
                    'allow_fractions': True
                }
            }
        )
        GradeTool.objects.get_or_create(grade=grade2_prep, tool=solver)
        GradeTool.objects.get_or_create(grade=grade2_prep, tool=geometry)
        GradeTool.objects.get_or_create(grade=grade2_prep, tool=graph)

        # Grade 3 Prep Config
        GradeTool.objects.get_or_create(
            grade=grade3_prep,
            tool=calc,
            defaults={
                'config_json': {
                    'allow_trig': True, 
                    'allow_roots': True,
                    'allow_fractions': True
                }
            }
        )
        GradeTool.objects.get_or_create(grade=grade3_prep, tool=solver)
        GradeTool.objects.get_or_create(grade=grade3_prep, tool=geometry)
        GradeTool.objects.get_or_create(grade=grade3_prep, tool=graph)

        self.stdout.write(self.style.SUCCESS('Successfully seeded initial data'))
