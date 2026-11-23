from datetime import date, timedelta
from decimal import Decimal

from django.db.models import Avg, Count, Exists, OuterRef, Q, Sum
from django.db.models.functions import ExtractHour, ExtractIsoWeekDay, TruncDate
from django.utils import timezone

from .models import Booking, Notification, Review


def financial_reference(bookings):
    amounts = bookings.aggregate(
        gmv=Sum('amount', filter=Q(status=Booking.Status.RESERVED), default=0),
        attended=Sum('amount', filter=Q(attendance_recorded=True), default=0),
        demo_records=Count('pk', filter=Q(schedule__activity__demo_data=True)),
    )
    amounts['estimated_commission'] = Decimal(amounts['attended']) * Decimal('0.10')
    return amounts


def period_controls():
    today = timezone.localdate()
    return {
        'today': today,
        'periods': [
            ('7 días', today - timedelta(days=6)),
            ('30 días', today - timedelta(days=29)),
            ('90 días', today - timedelta(days=89)),
            ('Este mes', today.replace(day=1)),
            ('Este año', today.replace(month=1, day=1)),
        ],
    }


def previous_period_count(query, params):
    try:
        start = date.fromisoformat(params.get('from', ''))
        end = date.fromisoformat(params.get('to', ''))
        if end < start:
            return None
        previous_start = start - (end - start) - timedelta(days=1)
    except (ValueError, OverflowError):
        return None
    return query.filter(created_at__date__gte=previous_start, created_at__date__lt=start).count()


def upcoming_capacity(slots):
    result = slots.aggregate(slots=Count('pk'), seats=Sum('capacity', default=0), available=Sum('available', default=0))
    result['used'] = result['seats'] - result['available']
    return result


def booking_timeline(bookings):
    days = list(
        bookings.filter(status=Booking.Status.RESERVED)
        .annotate(day=TruncDate('created_at')).values('day')
        .annotate(count=Count('pk'), attended=Count('pk', filter=Q(attendance_recorded=True)))
        .order_by('-day')[:12]
    )
    days.reverse()
    if not days:
        return None
    peak = max(row['count'] for row in days)
    points = []
    attendance = []
    for index, row in enumerate(days):
        x = 325 if len(days) == 1 else 36 + round(index * 578 / (len(days) - 1))
        row['x'] = x
        row['y'] = 150 - round(row['count'] * 120 / peak)
        row['attendance_y'] = 150 - round(row['attended'] * 120 / peak)
        row['tick'] = index == len(days) - 1 or index % (3 if len(days) > 8 else 2) == 0
        points.append(f"{x},{row['y']}")
        attendance.append(f"{x},{row['attendance_y']}")
    fill = f"{days[0]['x']},150 {' '.join(points)} {days[-1]['x']},150"
    return {'days': days, 'peak': peak, 'line': ' '.join(points), 'attendance': ' '.join(attendance), 'fill': fill}


def hourly_demand(bookings):
    groups = bookings.annotate(
        day=ExtractIsoWeekDay('schedule__starts_at'), hour=ExtractHour('schedule__starts_at'),
    ).order_by().values_list('day', 'hour').annotate(total=Count('pk'))
    counts = {}
    for day, hour, total in groups:
        key = (day, hour // 3)
        counts[key] = counts.get(key, 0) + total
    peak = max(counts.values(), default=0)
    days = ('Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo')
    first_block = min((block for _, block in counts), default=2)
    blocks = range(min(first_block, 2), 8)
    rows = []
    for day, label in enumerate(days, start=1):
        cells = []
        for block in blocks:
            count = counts.get((day, block), 0)
            level = (count * 4 + peak - 1) // peak if peak else 0
            cells.append((count, level))
        rows.append((label[:3], cells))
    top = min((key for key, value in counts.items() if value == peak), default=None)
    return {
        'hours': [block * 3 for block in blocks], 'rows': rows, 'peak': peak,
        'peak_day': days[top[0] - 1] if top else None, 'peak_hour': top[1] * 3 if top else None,
    }


def workshop_rows(bookings):
    return (
        bookings.order_by().values('schedule__activity__name', 'schedule__activity_id')
        .annotate(reserved=Count('pk', filter=Q(status=Booking.Status.RESERVED)),
                  cancelled=Count('pk', filter=Q(status=Booking.Status.CANCELLED)),
                  attended=Count('pk', filter=Q(attendance_recorded=True)),
                  demo_amount=Sum('amount', filter=Q(status=Booking.Status.RESERVED), default=0))
        .order_by('-reserved', 'schedule__activity__name', 'schedule__activity_id')
    )


def center_metrics(bookings, slots, previous):
    valid = bookings.filter(status=Booking.Status.RESERVED)
    cancelled_by_center = Notification.objects.filter(
        booking_id=OuterRef('pk'), kind=Notification.Kind.SCHEDULE_CANCELLED,
    )
    counts = bookings.annotate(cancelled_with_notice=Exists(cancelled_by_center)).aggregate(
        total=Count('pk'),
        reserved=Count('pk', filter=Q(status=Booking.Status.RESERVED)),
        cancelled=Count('pk', filter=Q(status=Booking.Status.CANCELLED)),
        center_cancelled=Count('pk', filter=Q(status=Booking.Status.CANCELLED, cancelled_with_notice=True)),
        attended=Count('pk', filter=Q(attendance_recorded=True)),
        booking_amount=Sum('amount', filter=Q(status=Booking.Status.RESERVED), default=0),
        attended_amount=Sum('amount', filter=Q(attendance_recorded=True), default=0),
    )
    counts['other_cancelled'] = counts['cancelled'] - counts['center_cancelled']
    counts['ticket'] = counts['booking_amount'] / counts['reserved'] if counts['reserved'] else None
    families = list(valid.order_by().values('user_id').annotate(total=Count('pk')).values_list('total', flat=True))
    returning = sum(count > 1 for count in families)
    ratings = Review.objects.filter(booking__in=valid)
    scores = dict(ratings.order_by().values('rating').annotate(total=Count('pk')).values_list('rating', 'total'))
    cancellations = list(
        bookings.filter(status=Booking.Status.CANCELLED).annotate(from_center=Exists(cancelled_by_center))
        .filter(from_center=True).order_by().values('schedule__cancellation_reason')
        .annotate(total=Count('pk')).order_by('-total', 'schedule__cancellation_reason')[:5]
    )
    return {
        'counts': counts, 'capacity': upcoming_capacity(slots), 'prior_orders': previous,
        'families': len(families), 'returning': returning, 'one_booking': len(families) - returning,
        'rating': ratings.aggregate(value=Avg('rating'))['value'], 'rating_total': sum(scores.values()),
        'scores': [(score, scores.get(score, 0)) for score in range(5, 0, -1)],
        'timeline': booking_timeline(bookings),
        'limited_slots': slots.filter(available__lte=2).count(),
        'unanswered_reviews': ratings.filter(response='').count(),
        'heatmap': hourly_demand(valid), 'workshops': list(workshop_rows(bookings)[:12]), 'reasons': cancellations,
        'cancel_alert': counts['total'] and counts['cancelled'] * 100 > counts['total'] * 5,
    }
