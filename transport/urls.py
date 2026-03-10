from django.urls import path
from . import views

app_name = 'transport'

urlpatterns = [
    path('', views.home, name='home'),
    path('routes/', views.route_list, name='route_list'),
    path('routes/<int:pk>/', views.route_detail, name='route_detail'),
    path('stops/', views.stop_list, name='stop_list'),
    path('stops/<int:pk>/', views.stop_detail, name='stop_detail'),
    path('planner/', views.route_planner, name='route_planner'),
    path('map/', views.map_view, name='map_view'),
]
