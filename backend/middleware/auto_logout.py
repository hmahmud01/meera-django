import datetime
from django.conf import settings
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone
from django.urls import reverse

class AutoLogoutMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if not request.user.is_authenticated:
            return
        
        now = timezone.now()
        try:
            last_activity = request.session.get('last_activity')
            if last_activity:
                last_activity_time = timezone.datetime.fromisoformat(last_activity)

                if timezone.is_naive(last_activity_time):
                    last_activity_time = timezone.make_aware(last_activity_time)

                elapsed = (now - last_activity_time).total_seconds()

                if elapsed > settings.AUTO_LOGOUT_DELAY:
                    logout(request)
                    request.session.flush()
                    return redirect('/')  # make sure 'login' is the correct name

        except Exception:
            # If parsing fails, force logout for safety
            logout(request)
            request.session.flush()
            return redirect('/')  # make sure 'login' is the correct name

        # ✅ Always update the last activity if user is authenticated and not logged out
        request.session['last_activity'] = now.isoformat()