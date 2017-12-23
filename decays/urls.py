from django.conf.urls import url
from decays import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'accounts', views.UserView, 'list')

urlpatterns = [
    url(r'^api/decaytypelist/$', views.decay_type_list),
    url(r'^api/generateevent/$', views.generate_random_event),
    url(r'^useranalyzedevents/$', views.user_analyzed_events),
    url(r'^analyzedevents/$', views.AnalyzedEventList.as_view()),
    url(r'^analyzedevents/(?P<pk>[0-9]+)/$', views.AnalyzedEventDetail.as_view()),
    url(r'^institutions/$', views.InstitutionList.as_view()),
    url(r'^users/$', views.UserList.as_view()),
    url(r'^users/(?P<pk>[0-9]+)/$', views.UserDetail.as_view()),
    url(r'^usersthisinstitution/$', views.user_list_this_institution),
]

urlpatterns += router.urls
