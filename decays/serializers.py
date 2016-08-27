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