from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes

from rest_framework import permissions

from rest_framework.permissions import IsAuthenticated, IsAdminUser
from decays.permissions import IsOwnerOrReadOnly, IsLocalStaffOrOwner, IsLocalStaffOrOwnerTheseEvents

from decays.models import *
from decays.serializers import DecayTypeSerializer
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from django.utils.six import BytesIO

from rest_framework import generics
from django.contrib.auth.models import User
from decays.serializers import UserSerializer, AnalyzedEventSerializer, InstitutionSerializer

from django.http import HttpResponse
import json

import random

from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from .permissions import IsStaffOrTargetUser

# ISSUES(?):
# - at this point, when a new user is created, a hashed version of the new user's
#   password is returned to the client...is that bad?!?  probably!
# - when using postman to get a list of accounts, it is only requiring a user
#   to be logged in; it is not checking to see if the user is_staff



# https://richardtier.com/2014/02/25/django-rest-framework-user-endpoint/
class UserView(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    #model = User
    queryset = User.objects.all()

    def get_permissions(self):
        # allow non-authenticated user to create via POST
        return (AllowAny() if self.request.method == 'POST'
                else IsStaffOrTargetUser()),


@api_view()
def hello_world(request):
    return Response({"message": "Hello, world!"})


# to force authentication:
# http://www.django-rest-framework.org/api-guide/permissions/
# from rest_framework.decorators import api_view, permission_classes
# from rest_framework.permissions import IsAuthenticated
# @permission_classes((IsAuthenticated, ))
#
# NICE!!!
#
# WORKING HERE:
#  json field.... https://github.com/bradjasper/django-jsonfield
#

# I believe that the following has now been deprecated and has been replaced by user_list_this_institution
#class UserList(generics.ListAPIView):
#    queryset = User.objects.all()
#    serializer_class = UserSerializer

class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated, IsLocalStaffOrOwner, )


# WORKING HERE:
# next...add class-based view(?) for AnalyzedEvents
# ...and an AnalyzedEvent serializer;
# possibly use the following: http://www.django-rest-framework.org/tutorial/3-class-based-views/#using-generic-class-based-views
# ...but don't forget this: http://www.django-rest-framework.org/tutorial/4-authentication-and-permissions/#associating-snippets-with-users


# maybe can use the @permission_classes decorator; also, maybe want to change
# to IsAuthenticated
class AnalyzedEventList(generics.ListCreateAPIView):
    queryset = AnalyzedEvent.objects.all()
    serializer_class = AnalyzedEventSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsLocalStaffOrOwnerTheseEvents, )
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class AnalyzedEventDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = AnalyzedEvent.objects.all()
    serializer_class = AnalyzedEventSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly, IsLocalStaffOrOwnerTheseEvents, )

class InstitutionList(generics.ListAPIView):
    queryset = Institution.objects.all()
    serializer_class = InstitutionSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


# to force authentication:
# http://www.django-rest-framework.org/api-guide/permissions/
# now, using httpie:
# http -a username:password GET http://127.0.0.1:8000/api/decaytypelist/
# ...gets in!
@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
def decay_type_list(request):
    """
    List all types of decays.
    """
    if request.method == 'GET':
        decay_types = DecayType.objects.all()
        serializer = DecayTypeSerializer(decay_types, many=True)
        return Response(serializer.data)

@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
def user_analyzed_events(request):
    """
    Gets all events for the currently authenticated user.
    """
    print request.user
    analyzed_events_queryset = AnalyzedEvent.objects.all().filter(owner=request.user)
    analyzed_events = []
    for event in analyzed_events_queryset:
        # https://code.tutsplus.com/tutorials/how-to-work-with-json-data-using-python--cms-25758
        event_data = json.loads(event.event_data)
        analyzed_events.append({
            'created': event.created.isoformat(),
            'title': event_data['event']['name'],
            'id': event.id,
            'submitted': event.submitted})

    data_json = json.dumps(analyzed_events)

    return Response(data_json)



@api_view(['GET'])
@permission_classes((IsAuthenticated, IsAdminUser, ))
def user_list_this_institution(request):
    """
    Gets all the users for the institution to which the current user (who must be an admin) belongs
    """
    print request.user
    # https://stackoverflow.com/questions/14537113/django-filter-items-with-onetoone-relationship-to-group-of-users
    user_queryset = User.objects.all().filter(profile__institution=request.user.profile.institution)
    users = []
    for user in user_queryset:
        # https://code.tutsplus.com/tutorials/how-to-work-with-json-data-using-python--cms-25758
        number_events = AnalyzedEvent.objects.all().filter(owner=user).count()

       
 #fields = ('id', 'username','password', 'email', 'first_name', 'last_name', 'analyzed_events', 'institution_id', 'date_joined', 'is_staff')

        
        #event_data = json.loads(event.event_data)
        users.append({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'number_events': number_events,
            'institution_id': user.profile.institution.id,
            'institution_name': user.profile.institution.name})

    data_json = json.dumps(users)

    return Response(data_json)




@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
def generate_random_event(request):
    """
    Generate a random event.  b_field should be a number (strength of the B field in kG);
    b_direction should be either 'in' or 'out'.
    NOTE: At this point, b_field and b_direction are not being used; rather,
          an event is being generated, and the client-side code is determining
          everything having to do with the B field.
    """

    # helpful page: http://stackoverflow.com/questions/150505/capturing-url-parameters-in-request-get

    b_field = request.GET.get('b_field','')
    b_direction = request.GET.get('b_direction','')

    # print request.GET

    print 'B field: ', b_field # probably a string at this point....
    print 'B direction: ', b_direction

    theta_min = 0.25
    theta_max = 0.85
    theta_lab = random.random()*(theta_max-theta_min)+theta_min
    sign_choices = [1, -1]
    theta_lab = random.choice(sign_choices)*theta_lab
    # this approach to generating random theta_lab values means that
    # there won't be incident particles in the "+y" direction

    id_list = []
    for decay_type in DecayType.objects.all():
        id_list.append(decay_type.id)

    pk = random.choice(id_list)

    decay_type = DecayType.objects.get(pk=pk)

    parent_mass = decay_type.parent.mass

    print "parent_mass: ", parent_mass

    # reduce xi_max for heavier initial particles....
    xi_max_initial_calc = 0.3-0.25*parent_mass/1900

    xi_min = 0.05

    if xi_max_initial_calc > xi_min:
        xi_max = min(0.3,xi_max_initial_calc)
    else:
        xi_max = xi_min

    print "xi_max: ", xi_max

    xi_lab = random.random()*(xi_max-xi_min)+xi_min

    print "xi_lab: ", xi_lab

    data = decay_type.rand_momentum_config_parent_cm(xi_lab, theta_lab)

    # if this is a two-step decay, will need to get the "data" in two steps...not too bad, though!

    data_json = json.dumps(data)

    print data_json

    context = {'data': data}

    return Response(data_json)

#
# MAKE SURE the user is logged in first...?  maybe don't need to do that for simple get requests like this....

# NEXT: add a function to the decay type model that computes a momentum configuration given
#       one or more angles, invariant masses, or something; and then one that calls this and
#       computes it randomly; then write an api for serving this up and a controller to go get it!
