from django.conf.urls import url
from decays import views

urlpatterns = [
    url(r'^api/decaytypelist/$', views.decay_type_list),
    url(r'^api/generateevent/$', views.generate_random_event),
]
