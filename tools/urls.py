from django.urls import path
from . import views

app_name = 'tools'

urlpatterns = [
    path('api/calculate/', views.CalculatorAPI.as_view(), name='api_calculator'),
    path('api/solve/', views.SolverAPI.as_view(), name='api_solve'),
    path('api/geometry/', views.GeometryAPI.as_view(), name='api_geometry'),
    path('api/probability/', views.ProbabilityAPI.as_view(), name='api_probability'),
    path('<slug:tool_slug>/', views.ToolView.as_view(), name='tool_view'),
]
