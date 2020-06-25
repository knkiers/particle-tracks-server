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
#from django.utils.six import BytesIO

from rest_framework import generics
from rest_framework_jwt.settings import api_settings


from django.contrib.auth.models import User
from decays.serializers import UserSerializer, AnalyzedEventSerializer, InstitutionSerializer

from django.http import HttpResponse
import json

import random

from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework import status

from .permissions import IsStaffOrTargetUser, IsLocalStaffOrTargetUser

# ISSUES(?):
# - at this point, when a new user is created, a hashed version of the new user's
#   password is returned to the client...is that bad?!?  probably!
# - when using postman to get a list of accounts, it is only requiring a user
#   to be logged in; it is not checking to see if the user is_staff



# https://richardtier.com/2014/02/25/django-rest-framework-user-endpoint/
class UserView(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    #model = User
    #queryset = User.objects.all()

    # http://masnun.rocks/2017/03/27/django-rest-framework-using-request-object/
    def get_queryset(self):
            queryset = User.objects.all().filter(profile__institution=self.request.user.profile.institution)
            return queryset

    def get_permissions(self):
        # allow non-authenticated user to create via POST
        if self.request.method == 'POST':
            return (AllowAny()),
        elif self.request.method == 'GET':
            return (IsLocalStaffOrTargetUser()),
        else:
            return (IsLocalStaffOrOwner()),


            # try IsLocalStaffOrOwner....(?)maybe let this only be for the user


        #elif self.request.method == 'PUT':
        #    return (IsStaffOrTargetUserUpdateOnly()),

        #return (AllowAny() if self.request.method == 'POST'
        #        else IsStaffOrTargetUser()),

    # https://thinkster.io/tutorials/django-json-api/authentication
    def update(self, request, *args, **kwargs):

        serializer_data = request.data

        # Here is that serialize, validate, save pattern we talked about
        # before.
        serializer = self.serializer_class(
            request.user, data=serializer_data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()

        # Generate a new token
        # http://getblimp.github.io/django-rest-framework-jwt/#refresh-token
        # https://stackoverflow.com/questions/44820130/how-to-handle-token-when-update-username-field-with-django-rest-framework
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(instance)
        token = jwt_encode_handler(payload)

        #return Response({'token': token.decode('unicode_escape')}, status=status.HTTP_200_OK)
        return Response({'token': token}, status=status.HTTP_200_OK)


# WORKING HERE....password reset: https://github.com/anx-ckreuzberger/django-rest-passwordreset


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
    print(request.user)
    analyzed_events_queryset = AnalyzedEvent.objects.all().filter(owner=request.user)
    analyzed_events = []
    for event in analyzed_events_queryset:
        # https://code.tutsplus.com/tutorials/how-to-work-with-json-data-using-python--cms-25758
        event_data = json.loads(event.event_data)
        analyzed_events.append({
            'updated': event.updated.isoformat(),
            'created': event.created.isoformat(),
            'title': event_data['event']['name'],
            'id': event.id,
            'submitted': event.submitted})
    #data_json = json.dumps(analyzed_events)
    #print(analyzed_events)
    return Response(analyzed_events)



@api_view(['GET'])
@permission_classes((IsAuthenticated, IsAdminUser, ))
def user_list_this_institution(request):
    """
    Gets all the users for the institution to which the current user (who must be an admin) belongs
    """
    print(request.user)
    # https://stackoverflow.com/questions/14537113/django-filter-items-with-onetoone-relationship-to-group-of-users
    user_queryset = User.objects.all().filter(profile__institution=request.user.profile.institution)
    users = []
    for user in user_queryset:
        # https://code.tutsplus.com/tutorials/how-to-work-with-json-data-using-python--cms-25758
        number_events = AnalyzedEvent.objects.all().filter(owner=user).count()
        # https://stackoverflow.com/questions/9834038/django-order-by-query-set-ascending-and-descending
        dates = [event.updated for event in AnalyzedEvent.objects.all().filter(owner=user).order_by('-updated')]
        if len(dates) > 0:
            latest_activity = dates[0]
        else:
            latest_activity = user.date_joined
        #print(user, "  ", latest_activity)
        #print(dates)

       
 #fields = ('id', 'username','password', 'email', 'first_name', 'last_name', 'analyzed_events', 'institution_id', 'date_joined', 'is_staff')

        
        #event_data = json.loads(event.event_data)
        users.append({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'latest_activity': latest_activity,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'number_events': number_events,
            'institution_id': user.profile.institution.id,
            'institution_name': user.profile.institution.name})

    #data_json = json.dumps(users)

    return Response({
        'users': users,
        'institution': request.user.profile.institution.name})


@api_view(['GET'])
@permission_classes((AllowAny,))
def events_with_same_signature(request, id):
    """
    Returns a list of events that have the same event signature as the one
    whose id is in the request.
    """

    print('id: ', id)

    target_decay = DecayType.objects.get(pk=id)

    print('decay type: ', target_decay)
    print(target_decay.parent)
    print(target_decay.daughter_one)
    print(target_decay.daughter_two)
    print(target_decay.daughter_three)

    all_decays = DecayType.objects.all()

    # number of particles in final state agree
    decays_same_signature_first_pass = [dt for dt in all_decays if (dt.is_two_body_decay() == target_decay.is_two_body_decay())]

    print(decays_same_signature_first_pass)

    if target_decay.parent_alias == None:
        # parent's identity is known
        print('parent identity is known; must be an exact match')
        decays_same_signature_second_pass = [dt for dt in decays_same_signature_first_pass if dt.parent == target_decay.parent]
    else:
        print('parent identity is not know; only the charge needs to match')
        decays_same_signature_second_pass = [dt for dt in decays_same_signature_first_pass if dt.parent.charge == target_decay.parent.charge]

    print(decays_same_signature_second_pass)
    
    for dt in decays_same_signature_second_pass:
        print(dt.id, " ", dt.parent, " ", dt.daughter_one, " ", dt.daughter_two, " ", dt.daughter_three)

    # at this point, the parents match....
    matching_decays = []
    for dt in decays_same_signature_second_pass:
        print('candidate decay id: ', dt.id)
        dt_list = [
            {
                'id': dt.daughter_one.id,
                'charge': dt.daughter_one.charge
            },
            {
                'id': dt.daughter_two.id,
                'charge': dt.daughter_two.charge
            },
        ]
        if dt.daughter_three != None:
            dt_list.append({
                'id': dt.daughter_three.id,
                'charge': dt.daughter_three.charge
            })
        
        # need to go through the list of daughter particles twice....first only do the "known" ones, then do the not-known ones;
        # the reason is that if we have a not-known one, we could accidentally pop an exact match out of the list and lead to a false negative

        decay_type_matches = True

        # first do the ones that do not have aliases, then go through again and do the ones that do have aliases...kind of painful....
        if decay_type_matches and (target_decay.daughter_one_alias == None):
            print('daughter one is known')
            result = pop_matching_decays(True, target_decay.daughter_one, dt_list)
            dt_list = result['remaining_particles']
            if not result['dt_matches']:
                decay_type_matches = False
        
        if decay_type_matches and (target_decay.daughter_two_alias == None):
            print('daughter two is known')
            result = pop_matching_decays(True, target_decay.daughter_two, dt_list)
            dt_list = result['remaining_particles']
            if not result['dt_matches']:
                decay_type_matches = False

        if (not target_decay.is_two_body_decay()) and decay_type_matches and (target_decay.daughter_three_alias == None):
            print('daughter three is known')
            result = pop_matching_decays(True, target_decay.daughter_three, dt_list)
            dt_list = result['remaining_particles']
            if not result['dt_matches']:
                decay_type_matches = False

        # now do the cases for which the particles have aliases....
        if decay_type_matches and (target_decay.daughter_one_alias != None):
            print('daughter one has an alias')
            result = pop_matching_decays(False, target_decay.daughter_one, dt_list)
            dt_list = result['remaining_particles']
            if not result['dt_matches']:
                decay_type_matches = False
        
        if decay_type_matches and (target_decay.daughter_two_alias != None):
            print('daughter two has an alias')
            result = pop_matching_decays(False, target_decay.daughter_two, dt_list)
            dt_list = result['remaining_particles']
            if not result['dt_matches']:
                decay_type_matches = False

        if (not target_decay.is_two_body_decay()) and decay_type_matches and (target_decay.daughter_three_alias != None):
            print('daughter three has an alias')
            result = pop_matching_decays(False, target_decay.daughter_three, dt_list)
            dt_list = result['remaining_particles']
            if not result['dt_matches']:
                decay_type_matches = False

        if decay_type_matches:
            print('>>> we have a total match!!!!')
            if target_decay.is_two_body_decay():
                matching_decays.append({
                    'decay_id': dt.id,
                    'parent_id': dt.parent.id,
                    'daughter_ids': [dt.daughter_one.id, dt.daughter_two.id]
                })
            else:
                matching_decays.append({
                    'decay_id': dt.id,
                    'parent_id': dt.parent.id,
                    'daughter_ids': [dt.daughter_one.id, dt.daughter_two.id, dt.daughter_three.id]
                })

    # Now need to reduce the list down to only the truly different types of decays.  So far we have decay types that might
    # actually represent the same decays, but have different particles that have aliases.
    
    # cycle through the list and check elements further down the list for matches.  If one of them is a match, add it
    # to a list of elements that will be removed, but don't pop it yet (or else might mess up the list that we're iterating
    # through).  Then go through the list and collect only those elements that remain.

    element_indices_to_be_deleted = []

    print('<><><> matching decays: ', matching_decays)

    for ii, elem in enumerate(matching_decays, start = 0):
        for jj in range(ii+1,len(matching_decays)):
            if (elem['parent_id'] == matching_decays[jj]['parent_id']) and list_elements_match_exactly(elem['daughter_ids'], matching_decays[jj]['daughter_ids']):
                print('>>> need to delete this element!')
                element_indices_to_be_deleted.append(jj)

    final_matching_decays = []
    # https://treyhunner.com/2016/04/how-to-loop-with-indexes-in-python/
    for ii, elem in enumerate(matching_decays, start = 0):
        # https://thispointer.com/python-how-to-check-if-an-item-exists-in-list-search-by-value-or-condition/#:~:text=Check%20if%20element%20exist%20in%20list%20using%20list.&text=count(element)%20function%20returns%20the,given%20element%20exists%20in%20list.
        if element_indices_to_be_deleted.count(ii) == 0: 
            parent = Particle.objects.get(pk=elem['parent_id'])
            final_matching_decays.append({
                'decay_id': elem['decay_id'],
                'parent': {
                    'id': parent.id,
                    'mass': parent.mass,
                    'name': parent.name,
                    'verbose_name': parent.verbose_name,
                    'charge': parent.charge
                },
                'decay_products': [{
                    'id': daughter.id, 
                    'mass': daughter.mass,
                    'name': daughter.name,
                    'verbose_name': daughter.verbose_name,
                    'charge': daughter.charge
                } for daughter in [Particle.objects.get(pk=daughter_id) for daughter_id in elem['daughter_ids']]],
                'name': DecayType.objects.get(pk=elem['decay_id']).name_without_aliases
            })
    
    print('final matching decays list! ', final_matching_decays)

    if target_decay.is_two_body_decay():
        target_daugther_id_list = [target_decay.daughter_one.id, target_decay.daughter_two.id]
    else:
        target_daugther_id_list = [target_decay.daughter_one.id, target_decay.daughter_two.id, target_decay.daughter_three.id]

    original_decay = {
        'decay_id': target_decay.id,
        'parent': {
            'id': target_decay.parent.id,
            'mass': target_decay.parent.mass,
            'name': target_decay.parent.name,
            'verbose_name': target_decay.parent.verbose_name,
            'charge': target_decay.parent.charge
        },
        'decay_products': [{
                    'id': daughter.id, 
                    'mass': daughter.mass,
                    'name': daughter.name,
                    'verbose_name': daughter.verbose_name,
                    'charge': daughter.charge
                } for daughter in [Particle.objects.get(pk=daughter_id) for daughter_id in target_daugther_id_list]],
        'name': DecayType.objects.get(pk=target_decay.id).name_without_aliases
    }
    
    return Response({'original_decay': original_decay, 'matching_decays': final_matching_decays})

def pop_matching_decays(target_particle_known, target_decay_particle, decay_type_list):

    print('target particle known: ', target_particle_known)
    print('target particle id: ', target_decay_particle.id)
    print('target particle charge: ', target_decay_particle.charge)

    dt_matches = True
    matching_index = -1
    if target_particle_known:
        # ids must match
        print('particle ids must match!')
        for ii, elem in enumerate(decay_type_list, start=0):
            print('decay id: ', elem['id'])
            if elem['id'] == target_decay_particle.id:
                matching_index = ii
                print('we have a match! ', matching_index)
    else:
        print('particle charges must match')
        for ii, elem in enumerate(decay_type_list, start=0):
            print('decay charge: ', elem['charge'])
            if elem['charge'] == target_decay_particle.charge:
                matching_index = ii
                print('we have a match! ', matching_index)

    if matching_index > -1:
        decay_type_list.pop(matching_index)
    else:
        dt_matches = False
    return {'dt_matches': dt_matches, 'remaining_particles': decay_type_list}

def list_elements_match_exactly(list_one, list_two):
    """
    list_one and list_two are assumed to be lists of integers.  This method checks if they contain 
    exactly the same integers (although possibly in a different order).
    """

    # make a copy of list_two, since it is passed in by reference
    new_list_two = []
    for elem in list_two:
        new_list_two.append(elem)

    if len(list_one) != len(new_list_two):
        return False
    
    for elem in list_one:
        try:
            ii = new_list_two.index(elem)
            new_list_two.pop(ii)
        except:
            return False
    
    return True

@api_view(['GET'])
#@permission_classes((IsAuthenticated, ))
@permission_classes((AllowAny,))
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

    print('B field: ', b_field) # probably a string at this point....
    print('B direction: ', b_direction)

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

    print("parent_mass: ", parent_mass)

    # reduce xi_max for heavier initial particles....
    xi_max_initial_calc = 0.3-0.25*parent_mass/1900

    xi_min = 0.05

    if xi_max_initial_calc > xi_min:
        xi_max = min(0.3,xi_max_initial_calc)
    else:
        xi_max = xi_min

    print("xi_max: ", xi_max)

    xi_lab = random.random()*(xi_max-xi_min)+xi_min

    print("xi_lab: ", xi_lab)

    data = decay_type.rand_momentum_config_parent_cm(xi_lab, theta_lab)

    # if this is a two-step decay, will need to get the "data" in two steps...not too bad, though!

    #data_json = json.dumps(data)
    print(data)
    #print(data_json)

    #context = {'data': data}

    #return Response(data_json)
    return Response(data)

#
# MAKE SURE the user is logged in first...?  maybe don't need to do that for simple get requests like this....

# NEXT: add a function to the decay type model that computes a momentum configuration given
#       one or more angles, invariant masses, or something; and then one that calls this and
#       computes it randomly; then write an api for serving this up and a controller to go get it!
