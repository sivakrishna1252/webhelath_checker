"""
URL configuration for the monitoring app.
"""
from django.urls import path
from . import views

app_name = 'monitoring'

urlpatterns = [
    # Main pages
    path('', views.status_page, name='status_page'),
    path('alerts/', views.alerts_page, name='alerts_page'),
    
    # Website management
    path('website/add/', views.add_website, name='add_website'),
    path('website/<int:website_id>/', views.website_detail, name='website_detail'),
    path('website/<int:website_id>/edit/', views.edit_website, name='edit_website'),
    path('website/<int:website_id>/delete/', views.delete_website, name='delete_website'),
    path('website/<int:website_id>/check/', views.manual_check, name='manual_check'),
    
    # Internal app management
    path('website/<int:website_id>/internal-app/add/', views.add_internal_app, name='add_internal_app'),
    path('internal-app/<int:internal_app_id>/edit/', views.edit_internal_app, name='edit_internal_app'),
    path('internal-app/<int:internal_app_id>/delete/', views.delete_internal_app, name='delete_internal_app'),
    
    # API endpoints
    path('api/status/', views.api_status, name='api_status'),
    
    # Alert management
    path('alert/<int:alert_id>/clear/', views.clear_alert, name='clear_alert'),
    path('alerts/clear-all/', views.clear_all_alerts, name='clear_all_alerts'),
]



#urls wil be working