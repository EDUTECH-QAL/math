from django.db import models
from grades.models import Grade

class Tool(models.Model):
    TYPE_CHOICES = (
        ('CALC', 'Calculator'),
        ('SOLVER', 'Equation Solver'),
        ('GEO', 'Geometry'),
        ('GRAPH', 'Graphing'),
        ('UNIT', 'Unit Converter'),
        ('MATRIX', 'Matrix Calculator'),
        ('PROB', 'Probability Simulator'),
        ('OTHER', 'Other'),
    )

    name_en = models.CharField(max_length=100)
    name_ar = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    tool_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='OTHER')
    description_en = models.TextField(blank=True)
    description_ar = models.TextField(blank=True)
    icon_name = models.CharField(max_length=50, help_text="CSS class or filename for icon")
    
    # Many-to-Many with Grade through GradeTool
    grades = models.ManyToManyField(Grade, through='GradeTool', related_name='tools')

    def __str__(self):
        return self.name_en

class GradeTool(models.Model):
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE)
    tool = models.ForeignKey(Tool, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    config_json = models.JSONField(default=dict, blank=True, help_text="Specific configuration for this tool for this grade")

    class Meta:
        unique_together = ('grade', 'tool')
        verbose_name = "Grade Tool Configuration"
        verbose_name_plural = "Grade Tool Configurations"

    def __str__(self):
        return f"{self.tool.name_en} for {self.grade.name_en}"
