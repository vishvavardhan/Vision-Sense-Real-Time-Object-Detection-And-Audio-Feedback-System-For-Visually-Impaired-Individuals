"""
URL configuration for object_detection project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path


from django.conf import settings
from django.conf.urls.static import static

from userapp import views as userviews

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',userviews.index,name="index"),
    path('about/',userviews.about,name="about"),
    path('login/',userviews.login,name="login"),
    path("register/",userviews.register,name="register"),
    path("contact/",userviews.contact,name="contact"),
    path("user/otp/",userviews.otp,name="otp"),
    path("user/dashboard/",userviews.dashboard,name="dashboard"),
    path("user/profile/",userviews.profile,name="profile"),
    path('user/logout/',userviews.user_logout,name="user_logout"),
    path('start_object_detection/', userviews.start_object_detection, name='start_object_detection'),
    path('detect-objects/', userviews.detect_objects, name='detect_objects'),
    path('video_feed/', userviews.video_feed, name='video_feed'),



]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
