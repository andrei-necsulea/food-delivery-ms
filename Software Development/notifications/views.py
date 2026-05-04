
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Notification
from accounts.decorators import role_required


@role_required(['admin', 'manager', 'client', 'driver'])
def notification_list(request):
    """Display list of notifications for the current user"""
    notifications = Notification.objects.filter(user=request.user)

    # Mark notifications as read when viewed (optional - could be done via AJAX)
    unread_count = notifications.filter(is_read=False).count()

    return render(request, 'notifications/notification_list.html', {
        'notifications': notifications,
        'unread_count': unread_count,
    })


@role_required(['admin', 'manager', 'client', 'driver'])
def mark_as_read(request, notification_id):
    """Mark a specific notification as read"""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True})

    return redirect('notification_list')


@role_required(['admin', 'manager', 'client', 'driver'])
def mark_all_as_read(request):
    """Mark all notifications as read for current user"""
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True})

    messages.success(request, 'All notifications marked as read.')
    return redirect('notification_list')


@role_required(['admin', 'manager', 'client', 'driver'])
def delete_notification(request, notification_id):
    """Delete a specific notification"""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.delete()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True})

    messages.success(request, 'Notification deleted.')
    return redirect('notification_list')


def get_unread_count(request):
    """AJAX endpoint to get unread notification count"""
    if request.user.is_authenticated:
        count = Notification.objects.filter(user=request.user, is_read=False).count()
        return JsonResponse({'unread_count': count})
    return JsonResponse({'unread_count': 0})
