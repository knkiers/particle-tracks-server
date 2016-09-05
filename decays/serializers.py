from rest_framework import serializers
from decays.models import DecayType

class DecayTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DecayType
        fields = ('id','parent','parent_alias',
                  'daughter_one','daughter_one_alias',
                  'daughter_two','daughter_two_alias',
                  'daughter_three','daughter_three_alias',
                  'name')

from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
  #snippets = serializers.PrimaryKeyRelatedField(many=True, queryset=Snippet.objects.all())

  class Meta:
      model = User
      fields = ('id', 'username')
      #, 'snippets')