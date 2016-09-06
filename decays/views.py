from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes

from rest_framework.permissions import IsAuthenticated

from decays.models import *
from decays.serializers import DecayTypeSerializer
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from django.utils.six import BytesIO

from rest_framework import generics
from django.contrib.auth.models import User
from decays.serializers import UserSerializer

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
# WORKING HERE: add log in, etc., and try to make decay_type_list only
#               accessible if the person is logged in....
# ALSO: json field.... https://github.com/bradjasper/django-jsonfield
#

class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

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
def generate_random_event(request):
    """
    Generate a random event.  b_field should be a number (strength of the B field in kG);
    b_direction should be either 'in' or 'out'.
    """

    # helpful page: http://stackoverflow.com/questions/150505/capturing-url-parameters-in-request-get

    b_field = request.GET.get('b_field','')
    b_direction = request.GET.get('b_direction','')

    # print request.GET

    print b_field # probably a string at this point....
    print b_direction

    xi_min = 0.05
    xi_max = 0.3
    xi_lab = random.random()*(xi_max-xi_min)+xi_min

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
