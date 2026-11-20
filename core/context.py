from .access import account_start


MANAGEMENT_ROUTES = frozenset({'management', 'create_record', 'edit_record', 'cancel_schedule'})
WORKSPACE_GROUP_ROUTES = {
    'data': MANAGEMENT_ROUTES,
    'performance': {'reputation', 'reply_review', 'finance', 'withdrawal', 'bank'},
    'account': {'profile', 'password_change'},
}
PROVIDER_WORKSPACE_ROUTES = MANAGEMENT_ROUTES | WORKSPACE_GROUP_ROUTES['performance'] | WORKSPACE_GROUP_ROUTES['account'] | {
    'dashboard', 'bookings', 'requests', 'request_create', 'request_detail',
    'notifications',
}


def portal(request):
    match = request.resolver_match
    route = match.url_name if match else None
    role = request.user.role if request.user.is_authenticated else None
    return {
        'academic_demo': True,
        'account_start': account_start(request.user) if role else None,
        'workspace_navigation': (
            role == 'admin'
            or (role == 'provider' and route in PROVIDER_WORKSPACE_ROUTES)
            or (role == 'superadmin' and (route in MANAGEMENT_ROUTES or route == 'platform_statistics'))
        ),
        'workspace_group': next((group for group, routes in WORKSPACE_GROUP_ROUTES.items() if route in routes), 'operations'),
        'workspace_kind': 'schedules' if route == 'cancel_schedule' else match.kwargs.get('kind') if match else None,
        'unread_notification_count': request.user.notifications.filter(read_at__isnull=True).count()
        if role else 0,
    }
