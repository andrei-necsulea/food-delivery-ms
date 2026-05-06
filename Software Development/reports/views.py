
from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Sum, Count, Avg, Q, F, ExpressionWrapper, DurationField
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages

from accounts.decorators import role_required
from orders.models import Order
from delivery.models import Delivery
from restaurants.models import Restaurant
from accounts.models import User
from .models import DailyAggregation, RestaurantMetrics, DriverMetrics
import json
from decimal import Decimal


def serialize_decimal(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError(f"Type {type(obj)} not serializable")


def format_duration_hhmm(duration):
    if not duration:
        return '-'

    total_seconds = int(duration.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    return f"{hours}h {minutes}m"


@role_required(['admin'])
def dashboard(request):
    """Admin dashboard with KPIs overview"""
    today = timezone.now().date()

    # Overall KPIs
    total_orders = Order.objects.count()
    total_revenue = Order.objects.aggregate(Sum('total_price'))['total_price__sum'] or 0
    completed_deliveries = Delivery.objects.filter(status='delivered').count()
    active_drivers = User.objects.filter(role='driver', is_active=True).count()

    # Today's data
    today_orders = Order.objects.filter(created_at__date=today).count()
    today_revenue = Order.objects.filter(created_at__date=today).aggregate(Sum('total_price'))['total_price__sum'] or 0
    today_completed = Delivery.objects.filter(status='delivered', created_at__date=today).count()

    # Last 7 days aggregation
    seven_days_ago = today - timedelta(days=7)
    daily_data = DailyAggregation.objects.filter(date__gte=seven_days_ago).order_by('date')

    dates = [str(d.date) for d in daily_data]
    orders_data = [d.total_orders for d in daily_data]
    revenue_data = [float(d.total_revenue) for d in daily_data]
    completed_data = [d.completed_deliveries for d in daily_data]

    return render(request, 'reports/dashboard.html', {
        'total_orders': total_orders,
        'total_revenue': float(total_revenue),
        'completed_deliveries': completed_deliveries,
        'active_drivers': active_drivers,
        'today_orders': today_orders,
        'today_revenue': float(today_revenue),
        'today_completed': today_completed,
        'chart_dates': json.dumps(dates),
        'chart_orders': json.dumps(orders_data),
        'chart_revenue': json.dumps(revenue_data),
        'chart_completed': json.dumps(completed_data),
    })


@role_required(['admin'])
def driver_performance_report(request):
    """Driver performance analytics"""
    drivers = User.objects.filter(role='driver')

    driver_stats = []
    for driver in drivers:
        total = Delivery.objects.filter(driver=driver).count()
        completed = Delivery.objects.filter(driver=driver, status='delivered').count()
        failed = Delivery.objects.filter(driver=driver, status__in=['cancelled', 'failed']).count()
        avg_duration = Delivery.objects.filter(
            driver=driver,
            status='delivered',
            completed_at__isnull=False,
        ).aggregate(
            avg_delivery_duration=Avg(
                ExpressionWrapper(F('completed_at') - F('created_at'), output_field=DurationField())
            )
        )['avg_delivery_duration']

        driver_stats.append({
            'driver': driver,
            'total_deliveries': total,
            'completed': completed,
            'failed': failed,
            'success_rate': (completed / total * 100) if total > 0 else 0,
            'avg_duration_display': format_duration_hhmm(avg_duration),
        })

    # Sort by success rate
    driver_stats.sort(key=lambda x: x['success_rate'], reverse=True)

    # Chart data
    driver_names = [d['driver'].username for d in driver_stats]
    completed_counts = [d['completed'] for d in driver_stats]
    failed_counts = [d['failed'] for d in driver_stats]

    return render(request, 'reports/driver_performance.html', {
        'driver_stats': driver_stats,
        'chart_drivers': json.dumps(driver_names),
        'chart_completed': json.dumps(completed_counts),
        'chart_failed': json.dumps(failed_counts),
    })


@role_required(['admin'])
def restaurant_sales_report(request):
    """Restaurant sales and performance analytics"""
    restaurants = Restaurant.objects.all()

    restaurant_stats = []
    for restaurant in restaurants:
        orders = Order.objects.filter(restaurant=restaurant)
        total_orders = orders.count()
        total_revenue = orders.aggregate(Sum('total_price'))['total_price__sum'] or 0
        avg_order_value = orders.aggregate(Avg('total_price'))['total_price__avg'] or 0

        restaurant_stats.append({
            'restaurant': restaurant,
            'total_orders': total_orders,
            'total_revenue': float(total_revenue),
            'avg_order_value': float(avg_order_value),
        })

    # Sort by revenue
    restaurant_stats.sort(key=lambda x: x['total_revenue'], reverse=True)

    # Chart data
    rest_names = [r['restaurant'].name for r in restaurant_stats]
    rest_orders = [r['total_orders'] for r in restaurant_stats]
    rest_revenue = [r['total_revenue'] for r in restaurant_stats]

    return render(request, 'reports/restaurant_sales.html', {
        'restaurant_stats': restaurant_stats,
        'chart_restaurants': json.dumps(rest_names),
        'chart_orders': json.dumps(rest_orders),
        'chart_revenue': json.dumps(rest_revenue),
    })


@role_required(['admin'])
def revenue_analytics(request):
    """Revenue analytics with daily/weekly/monthly breakdowns"""
    today = timezone.now().date()

    # Daily (last 30 days)
    thirty_days_ago = today - timedelta(days=30)
    daily_data = DailyAggregation.objects.filter(date__gte=thirty_days_ago).order_by('date')
    daily_dates = [str(d.date) for d in daily_data]
    daily_revenue = [float(d.total_revenue) for d in daily_data]

    # Weekly (last 12 weeks)
    weekly_data = []
    for i in range(12, 0, -1):
        week_start = today - timedelta(weeks=i)
        week_end = week_start + timedelta(weeks=1)
        revenue = DailyAggregation.objects.filter(
            date__gte=week_start, date__lt=week_end
        ).aggregate(Sum('total_revenue'))['total_revenue__sum'] or 0
        weekly_data.append({
            'week': f"Week {12 - i + 1}",
            'revenue': float(revenue)
        })

    weekly_labels = [w['week'] for w in weekly_data]
    weekly_revenue = [w['revenue'] for w in weekly_data]

    # Monthly (last 12 months)
    monthly_data = []
    for i in range(12, 0, -1):
        month_start = today - timedelta(days=30*i)
        month_end = month_start + timedelta(days=30)
        revenue = DailyAggregation.objects.filter(
            date__gte=month_start, date__lt=month_end
        ).aggregate(Sum('total_revenue'))['total_revenue__sum'] or 0
        monthly_data.append({
            'month': month_start.strftime('%b %Y'),
            'revenue': float(revenue)
        })

    monthly_labels = [m['month'] for m in monthly_data]
    monthly_revenue = [m['revenue'] for m in monthly_data]

    # Top metric
    total_revenue = sum(daily_revenue)
    avg_daily_revenue = total_revenue / len(daily_revenue) if daily_revenue else 0

    return render(request, 'reports/revenue_analytics.html', {
        'total_revenue': total_revenue,
        'avg_daily_revenue': avg_daily_revenue,
        'daily_labels': json.dumps(daily_dates),
        'daily_data': json.dumps(daily_revenue),
        'weekly_labels': json.dumps(weekly_labels),
        'weekly_data': json.dumps(weekly_revenue),
        'monthly_labels': json.dumps(monthly_labels),
        'monthly_data': json.dumps(monthly_revenue),
    })


@role_required(['admin'])
def order_analytics(request):
    """Order analytics: peak hours, customer segmentation, etc."""
    today = timezone.now().date()  # noqa: F841

    # Peak hours
    orders_by_hour = {}
    for i in range(24):
        orders_by_hour[i] = Order.objects.filter(
            created_at__hour=i
        ).count()

    hours = list(range(24))
    order_counts = [orders_by_hour[h] for h in hours]

    # Total metrics
    total_orders = Order.objects.count()
    avg_order_value = Order.objects.aggregate(Avg('total_price'))['total_price__avg'] or 0
    total_customers = User.objects.filter(role='client').count()

    # Orders by status
    status_dist = {}
    for status, _ in Order.STATUS_CHOICES:
        status_dist[status] = Order.objects.filter(status=status).count()

    status_labels = [s[0].replace('_', ' ').title() for s in Order.STATUS_CHOICES]
    status_counts = [status_dist[s[0]] for s in Order.STATUS_CHOICES]

    return render(request, 'reports/order_analytics.html', {
        'total_orders': total_orders,
        'avg_order_value': float(avg_order_value),
        'total_customers': total_customers,
        'hours': json.dumps(hours),
        'order_counts': json.dumps(order_counts),
        'status_labels': json.dumps(status_labels),
        'status_counts': json.dumps(status_counts),
    })


@role_required(['admin'])
def delivery_analytics(request):
    """Delivery analytics: success rate, avg time, etc."""
    today = timezone.now().date()

    # Delivery statistics
    total_deliveries = Delivery.objects.count()
    completed = Delivery.objects.filter(status='delivered').count()
    on_the_way = Delivery.objects.filter(status='on_the_way').count()
    assigned = Delivery.objects.filter(status='assigned').count()
    failed = total_deliveries - completed - on_the_way - assigned

    # Last 30 days breakdown
    thirty_days_ago = today - timedelta(days=30)
    daily_completed = []
    daily_labels = []

    for i in range(30):
        date = thirty_days_ago + timedelta(days=i)
        count = Delivery.objects.filter(status='delivered', created_at__date=date).count()
        daily_completed.append(count)
        daily_labels.append(str(date))

    # Status distribution
    status_dist = {
        'Completed': completed,
        'On The Way': on_the_way,
        'Assigned': assigned,
        'Failed/Cancelled': failed,
    }

    status_labels = list(status_dist.keys())
    status_counts = list(status_dist.values())

    success_rate = (completed / total_deliveries * 100) if total_deliveries > 0 else 0

    return render(request, 'reports/delivery_analytics.html', {
        'total_deliveries': total_deliveries,
        'completed': completed,
        'on_the_way': on_the_way,
        'assigned': assigned,
        'failed': failed,
        'success_rate': success_rate,
        'daily_labels': json.dumps(daily_labels),
        'daily_counts': json.dumps(daily_completed),
        'status_labels': json.dumps(status_labels),
        'status_counts': json.dumps(status_counts),
    })

