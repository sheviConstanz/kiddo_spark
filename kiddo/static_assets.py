from pathlib import PurePosixPath

from django.contrib.staticfiles.views import serve
from django.views.decorators.cache import never_cache


BROWSER_CONTENT_TYPES = {
    '.css': 'text/css',
    '.js': 'text/javascript',
    '.svg': 'image/svg+xml',
}


@never_cache
def serve_demo_asset(request, path):
    # Extracting a new ZIP can preserve timestamps from an older copy.
    request.META.pop('HTTP_IF_MODIFIED_SINCE', None)
    response = serve(request, path, insecure=True)
    response.headers.pop('Last-Modified', None)
    content_type = BROWSER_CONTENT_TYPES.get(PurePosixPath(path).suffix.lower())
    if content_type:
        response.headers['Content-Type'] = content_type
    return response
