from django.conf.urls import url
from decays import views

urlpatterns = [
    url(r'^api/decaytypelist/$', views.decay_type_list),
    url(r'^api/generateevent/$', views.generate_random_event),
    url(r'^users/$', views.UserList.as_view()),
    url(r'^users/(?P<pk>[0-9]+)/$', views.UserDetail.as_view()),
]
