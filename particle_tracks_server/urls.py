"""particle_tracks_server URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.urls import re_path, include
from django.contrib import admin
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    re_path(r'^admin/', admin.site.urls),
    re_path(r'^', include('decays.urls')),
    re_path(r'^api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    re_path(r'^api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    re_path(r'^api/password_reset/', include('django_rest_passwordreset.urls', namespace='password_reset')),
    re_path(r'^auth/', include('rest_framework.urls', namespace='rest_framework')),
]

# the following is to allow login/logout from the browsable api
urlpatterns += [
   # re_path(r'^api-auth/', include('rest_framework.urls',
   #                            namespace='rest_framework')),
]
