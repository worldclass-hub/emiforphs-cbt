from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

def redirect_to_dashboard_or_login(request):
    """Redirect to dashboard if logged in, else to login page"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('login')

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Root URL - checks if user is logged in
    path('', redirect_to_dashboard_or_login, name='home'),
    
    # Apps
    path('', include('accounts.urls')),
    path('teacher/', include('teacher_dashboard.urls')),
    path('student/', include('student_portal.urls')),  # Add this

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)