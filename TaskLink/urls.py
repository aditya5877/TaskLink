# D:\TaskLink\TaskLink\TaskLink\urls.py
from django.contrib import admin
from django.urls import path
from MyApp import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('services/', views.services, name='services'),
    path('worker/<int:worker_id>/', views.worker_profile, name='worker_profile'),
    path('login/', views.user_login, name='login'),
    path('register/', views.user_register, name='register'),
    path('verify_otp/', views.verify_otp, name='verify_otp'),
    path('logout/', views.user_logout, name='logout'),
    path('test_email/', views.test_email, name='test_email'),
    path('subscribe/', views.subscribe, name='subscribe'),
    path('subscribe_payment/', views.subscribe_payment, name='subscribe_payment'),
    path('profile/', views.profile, name='profile'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)