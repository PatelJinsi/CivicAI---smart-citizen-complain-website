from django.urls import path
from . import views

urlpatterns = [
    # Public
    path('', views.home, name='home'),

    # Auth
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Citizen
    path('submit/', views.submit_complaint, name='submit_complaint'),
    path('my-complaints/', views.my_complaints, name='my_complaints'),
    path('complaint/<int:pk>/', views.complaint_detail, name='complaint_detail'),

    # Admin
    path('dashboard/', views.dashboard, name='dashboard'),
    path('complaint/<int:pk>/status/', views.quick_status_update, name='quick_status_update'),
    path('complaint/<int:pk>/reanalyze/', views.reanalyze_complaint, name='reanalyze_complaint'),
]