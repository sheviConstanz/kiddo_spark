PANEL_ROUTES = frozenset({
    'dashboard', 'platform_statistics', 'profile', 'password_change', 'wallet',
    'bookings', 'review', 'reply_review', 'reputation', 'requests', 'request_detail',
    'management', 'create_record', 'edit_record', 'finance', 'withdrawal', 'bank',
    'provider_submissions', 'provider_submission', 'provider_review_queue', 'provider_review',
})


def portal(request):
    match = request.resolver_match
    route = match.url_name if match else None
    in_panel = route in PANEL_ROUTES or (route == 'explore' and bool(request.GET.get('favorites')))
    return {
        'academic_demo': True,
        'show_account_navigation': request.user.is_authenticated and in_panel,
    }
