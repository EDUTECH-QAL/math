from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('set-grade/<int:grade_id>/', views.SetGradeView.as_view(), name='set_grade'),
    path('set-language/<str:lang_code>/', views.SetLanguageView.as_view(), name='set_language'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
]
