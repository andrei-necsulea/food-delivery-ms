import logging
import time
import uuid
from contextvars import ContextVar


request_id_context_var = ContextVar('request_id', default='-')


class RequestIdFilter(logging.Filter):
    def filter(self, record):
        record.request_id = request_id_context_var.get()
        return True


class RequestLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger('fooddelivery.request')

    def __call__(self, request):
        request_id = str(uuid.uuid4())[:8]
        token = request_id_context_var.set(request_id)
        start = time.perf_counter()

        try:
            response = self.get_response(request)
            duration_ms = (time.perf_counter() - start) * 1000

            user_label = 'anonymous'
            if getattr(request, 'user', None) and request.user.is_authenticated:
                user_label = f"{request.user.username} ({request.user.role})"

            self.logger.info(
                '%s %s status=%s duration_ms=%.2f user=%s ip=%s',
                request.method,
                request.path,
                response.status_code,
                duration_ms,
                user_label,
                request.META.get('REMOTE_ADDR', '-'),
            )
            return response
        finally:
            request_id_context_var.reset(token)
