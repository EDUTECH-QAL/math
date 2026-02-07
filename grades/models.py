from django.db import models

class Grade(models.Model):
    STAGE_CHOICES = (
        ('PREP', 'Preparatory'),
        ('SEC', 'Secondary'),
    )

    name_en = models.CharField(max_length=100)
    name_ar = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    stage = models.CharField(max_length=10, choices=STAGE_CHOICES)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.name_en} ({self.get_stage_display()})"
