from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('crear/', views.crear_ticket, name='crear_ticket'),
    path('atender/<int:ticket_id>/', views.atender_ticket, name='atender_ticket'),
    path('atendidos/', views.tickets_atendidos, name='tickets_atendidos'),
    path('buscar/', views.buscar_ticket, name='buscar_ticket'),
    path(
        'listar-empleados/',
        views.ListEmpleadosPdf.as_view(),
        name='empleados_all'
    ), 
]
