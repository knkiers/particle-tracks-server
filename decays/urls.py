from django.urls import include, re_path
from decays import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'accounts', views.UserView, 'list')

urlpatterns = [
    re_path(r'^api/decaytypelist/$', views.decay_type_list),
    re_path(r'^api/generateevent/$', views.generate_random_event),
    re_path(r'^api/eventssamesignature/(\d+)/$', views.events_with_same_signature),
    re_path(r'^useranalyzedevents/$', views.user_analyzed_events),
    re_path(r'^analyzedevents/$', views.AnalyzedEventList.as_view()),
    re_path(r'^analyzedevents/(?P<pk>[0-9]+)/$', views.AnalyzedEventDetail.as_view()),
    re_path(r'^institutions/$', views.InstitutionList.as_view()),
    #re_path(r'^users/$', views.UserList.as_view()),
    re_path(r'^users/(?P<pk>[0-9]+)/$', views.UserDetail.as_view()),
    re_path(r'^usersthisinstitution/$', views.user_list_this_institution),
]

urlpatterns += router.urls
