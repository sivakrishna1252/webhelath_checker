"""
Views for the monitoring application.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Website, InternalApp, MonitoringCheck, AlertLog
from .services import MonitoringStats
from .forms import WebsiteForm, InternalAppForm
import json
from django.core.mail import send_mail
from django.conf import settings


def status_page(request):
    global_stats = MonitoringStats.get_global_stats()
    
    websites = Website.objects.all().prefetch_related('internal_apps')
    website_stats = []
    
    for website in websites:
        stats = MonitoringStats.get_website_stats(website)
        website_stats.append({
            'website': website,
            'stats': stats,
            'internal_apps': website.internal_apps.filter(is_active=True)
        })
    
    # Get recent alerts (only non-cleared ones for the dashboard)
    recent_alerts_qs = AlertLog.objects.filter(
        is_cleared=False,
        sent_at__gte=timezone.now() - timezone.timedelta(hours=24)
    ).order_by('-sent_at')
    
    recent_alerts_count = recent_alerts_qs.count()
    recent_alerts = recent_alerts_qs[:10]
    
    context = {
        'global_stats': global_stats,
        'website_stats': website_stats,
        'recent_alerts': recent_alerts,
        'recent_alerts_count': recent_alerts_count,
    }
    
    return render(request, 'monitoring/status_page.html', context)


def website_detail(request, website_id):
    website = get_object_or_404(Website, id=website_id)
    
    # Get website stats
    stats = MonitoringStats.get_website_stats(website)
    
    # Get recent checks
    recent_checks = MonitoringCheck.objects.filter(
        website=website
    ).order_by('-check_time')[:20]
    
    # Get internal apps
    internal_apps = website.internal_apps.filter(is_active=True)
    
    # Get recent alerts for this website (only non-cleared)
    recent_alerts_qs = AlertLog.objects.filter(
        website=website,
        is_cleared=False,
        sent_at__gte=timezone.now() - timezone.timedelta(days=7)
    ).order_by('-sent_at')
    
    recent_alerts_count = recent_alerts_qs.count()
    recent_alerts = recent_alerts_qs[:20]
    
    context = {
        'website': website,
        'stats': stats,
        'recent_checks': recent_checks,
        'internal_apps': internal_apps,
        'recent_alerts': recent_alerts,
        'recent_alerts_count': recent_alerts_count,
    }
    
    return render(request, 'monitoring/website_detail.html', context)


def add_website(request):
    if request.method == 'POST':
        form = WebsiteForm(request.POST)
        if form.is_valid():
            website = form.save()
                
            messages.success(request, f'Website "{website.name}" has been added successfully!')
            return redirect('monitoring:website_detail', website_id=website.id)
    else:
        form = WebsiteForm()
    
    return render(request, 'monitoring/add_website.html', {'form': form})


def edit_website(request, website_id):
    website = get_object_or_404(Website, id=website_id)
    
    if request.method == 'POST':
        form = WebsiteForm(request.POST, instance=website)
        if form.is_valid():
            form.save()
            messages.success(request, f'Website "{website.name}" has been updated successfully!')
            return redirect('monitoring:website_detail', website_id=website.id)
    else:
        form = WebsiteForm(instance=website)
    
    return render(request, 'monitoring/edit_website.html', {'form': form, 'website': website})


def add_internal_app(request, website_id):
    website = get_object_or_404(Website, id=website_id)
    
    if request.method == 'POST':
        form = InternalAppForm(request.POST)
        if form.is_valid():
            internal_app = form.save(commit=False)
            internal_app.website = website
            internal_app.save()
            messages.success(request, f'Internal app "{internal_app.name}" has been added successfully!')
            return redirect('monitoring:website_detail', website_id=website.id)
    else:
        form = InternalAppForm()
    
    return render(request, 'monitoring/add_internal_app.html', {'form': form, 'website': website})


def edit_internal_app(request, internal_app_id):
    internal_app = get_object_or_404(InternalApp, id=internal_app_id)
    
    if request.method == 'POST':
        form = InternalAppForm(request.POST, instance=internal_app)
        if form.is_valid():
            form.save()
            messages.success(request, f'Internal app "{internal_app.name}" has been updated successfully!')
            return redirect('monitoring:website_detail', website_id=internal_app.website.id)
    else:
        form = InternalAppForm(instance=internal_app)
    
    return render(request, 'monitoring/edit_internal_app.html', {'form': form, 'internal_app': internal_app})


def delete_website(request, website_id):
    website = get_object_or_404(Website, id=website_id)
    
    if request.method == 'POST':
        website_name = website.name
        website_url = website.url
        alert_email = website.alert_email
        
        website.delete()
        
        # Email is now handled by signals in monitoring/signals.py
        pass
            
        messages.success(request, f'Website "{website_name}" has been deleted successfully!')
        return redirect('monitoring:status_page')
    
    return render(request, 'monitoring/delete_website.html', {'website': website})


def delete_internal_app(request, internal_app_id):
    internal_app = get_object_or_404(InternalApp, id=internal_app_id)
    website = internal_app.website
    
    if request.method == 'POST':
        app_name = internal_app.name
        internal_app.delete()
        messages.success(request, f'Internal app "{app_name}" has been deleted successfully!')
        return redirect('monitoring:website_detail', website_id=website.id)
    
    return render(request, 'monitoring/delete_internal_app.html', {'internal_app': internal_app})


@csrf_exempt
@require_http_methods(["POST"])
def manual_check(request, website_id):
    website = get_object_or_404(Website, id=website_id)
    
    try:
        from .services import MonitoringService
        monitoring_service = MonitoringService()
        
        # Manually check this specific website
        monitoring_service.check_website(website)
        
        # Also manually check its active internal apps
        for app in website.internal_apps.filter(is_active=True):
            monitoring_service.check_internal_app(app)
        
        return JsonResponse({
            'success': True,
            'message': f'Manual check triggered for {website.name}'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error triggering check: {str(e)}'
        })


def api_status(request):
    global_stats = MonitoringStats.get_global_stats()
    
    websites = Website.objects.filter(status='active')
    website_data = []
    
    for website in websites:
        stats = MonitoringStats.get_website_stats(website)
        website_data.append({
            'id': website.id,
            'name': website.name,
            'url': website.url,
            'status': 'online' if website.is_online else 'offline',
            'uptime_percentage': stats['uptime_percentage'],
            'last_check': stats['last_check'].isoformat() if stats['last_check'] else None,
            'response_time': stats['avg_response_time']
        })
    
    return JsonResponse(
        {
            'global_stats': global_stats,
            'websites': website_data,
            'timestamp': timezone.now().isoformat(),
            'back_to_dashboard': request.build_absolute_uri('/')
        },
        json_dumps_params={'indent': 4}
    )


def alerts_page(request):
    alerts = AlertLog.objects.all().order_by('-sent_at')
    
    # Pagination
    paginator = Paginator(alerts, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Filtering
    search_query = request.GET.get('search', '')
    show_cleared = request.GET.get('show_cleared') == 'true'
    
    if not show_cleared:
        alerts = alerts.filter(is_cleared=False)
        
    if search_query:
        alerts = alerts.filter(
            Q(website__name__icontains=search_query) |
            Q(subject__icontains=search_query) |
            Q(message__icontains=search_query)
        )
    
    # Re-fetch page_obj after filtering
    paginator = Paginator(alerts, 50)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'show_cleared': show_cleared,
    }
    
    return render(request, 'monitoring/alerts_page.html', context)


@require_http_methods(["POST"])
def clear_alert(request, alert_id):
    alert = get_object_or_404(AlertLog, id=alert_id)
    alert.is_cleared = True
    alert.save()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.GET.get('ajax'):
        return JsonResponse({'success': True})
        
    messages.success(request, 'Alert cleared.')
    return redirect(request.META.get('HTTP_REFERER', 'monitoring:status_page'))


@require_http_methods(["POST"])
def clear_all_alerts(request):
    website_id = request.POST.get('website_id')
    
    if website_id:
        website = get_object_or_404(Website, id=website_id)
        AlertLog.objects.filter(website=website, is_cleared=False).update(is_cleared=True)
        messages.success(request, f'All alerts for {website.name} cleared.')
    else:
        AlertLog.objects.filter(is_cleared=False).update(is_cleared=True)
        messages.success(request, 'All alerts cleared.')
        
    return redirect(request.META.get('HTTP_REFERER', 'monitoring:status_page'))
