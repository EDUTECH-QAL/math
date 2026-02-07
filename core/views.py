from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import TemplateView
from grades.models import Grade

class HomeView(TemplateView):
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Group grades by stage for the UI
        context['prep_grades'] = Grade.objects.filter(stage='PREP')
        context['sec_grades'] = Grade.objects.filter(stage='SEC')
        return context

class SetGradeView(View):
    def get(self, request, grade_id):
        grade = get_object_or_404(Grade, id=grade_id)
        # Store selected grade in session
        request.session['grade_id'] = grade.id
        request.session['grade_name'] = grade.name_en # Or localized name based on pref
        return redirect('core:dashboard')

from django.utils import translation

class SetLanguageView(View):
    def get(self, request, lang_code):
        if lang_code in ['en', 'ar']:
            translation.activate(lang_code)
            # Use '_language' directly as LANGUAGE_SESSION_KEY might not be exposed in this Django version
            request.session['_language'] = lang_code
            # Also keep our custom key for backward compat if needed, or remove it
            request.session['lang'] = lang_code 
        
        # Redirect back to where they came from, or home
        referer = request.META.get('HTTP_REFERER', 'core:home')
        return redirect(referer)

class DashboardView(TemplateView):
    template_name = 'core/dashboard.html'

    def get(self, request, *args, **kwargs):
        # Ensure grade is selected
        grade_id = request.session.get('grade_id')
        if not grade_id:
            return redirect('core:home')
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        grade_id = self.request.session.get('grade_id')
        grade = get_object_or_404(Grade, id=grade_id)
        
        # Get tools for this grade
        context['grade'] = grade
        
        # Group tools by category
        tools = grade.tools.filter(gradetool__is_active=True).distinct()
        
        groups = {
            'algebra': {'title_en': 'Algebra', 'title_ar': 'الجبر', 'tools': [], 'icon': 'fa-calculator'},
            'geometry': {'title_en': 'Geometry', 'title_ar': 'الهندسة', 'tools': [], 'icon': 'fa-shapes'},
            'stats': {'title_en': 'Statistics & Probability', 'title_ar': 'الإحصاء والاحتمالات', 'tools': [], 'icon': 'fa-chart-pie'},
            'other': {'title_en': 'General Tools', 'title_ar': 'أدوات عامة', 'tools': [], 'icon': 'fa-toolbox'}
        }
        
        for tool in tools:
            if tool.tool_type in ['SOLVER', 'CALC', 'MATRIX']:
                groups['algebra']['tools'].append(tool)
            elif tool.tool_type in ['GEO', 'GRAPH']:
                groups['geometry']['tools'].append(tool)
            elif tool.tool_type in ['PROB']:
                groups['stats']['tools'].append(tool)
            else:
                groups['other']['tools'].append(tool)
                
        # Remove empty groups
        context['tool_groups'] = {k: v for k, v in groups.items() if v['tools']}
        
        # For backward compatibility if template not updated immediately (though we will update it)
        context['tools'] = tools
        return context
