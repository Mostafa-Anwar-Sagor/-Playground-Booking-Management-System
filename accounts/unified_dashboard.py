"""
Unified Dashboard System - Role-Based Dashboard Routing
Replaces Django Admin with Custom Dashboards
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden


@login_required
def unified_dashboard(request):
    """
    Unified dashboard entry point - routes users to appropriate dashboard based on role
    - Admin users -> Admin Dashboard with full platform control
    - Owner users -> Owner Dashboard with business management
    - Customer users -> User Dashboard with booking management
    """
    user = request.user
    
    # Route based on user type
    if user.user_type == 'admin':
        return redirect('accounts:admin_panel')
    elif user.user_type == 'owner':
        return redirect('accounts:owner_dashboard')
    else:  # customer
        return redirect('accounts:user_dashboard')


@login_required
def admin_panel_dashboard(request):
    """Admin dashboard with full platform management"""
    if request.user.user_type != 'admin':
        messages.error(request, 'Admin access required')
        return HttpResponseForbidden('Admin access required')
    
    # Render comprehensive admin dashboard
    return render(request, 'dashboard/admin_panel_full.html', {
        'user': request.user,
        'page_title': 'Admin Panel - Platform Management'
    })


@login_required
def owner_panel_dashboard(request):
    """Owner dashboard with business management"""
    if request.user.user_type != 'owner':
        messages.error(request, 'Owner access required')
        return HttpResponseForbidden('Owner access required')
    
    # Render comprehensive owner dashboard
    return render(request, 'dashboard/owner_panel_full.html', {
        'user': request.user,
        'page_title': 'Business Dashboard - Playground Management'
    })
