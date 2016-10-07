from rest_framework import serializers
from decays.models import DecayType, AnalyzedEvent
from django.contrib.auth.models import User

class DecayTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DecayType
        fields = ('id','parent','parent_alias',
                  'daughter_one','daughter_one_alias',
                  'daughter_two','daughter_two_alias',
                  'daughter_three','daughter_three_alias',
                  'name', 'human_readable_name')

# http://www.unknownerror.org/opensource/tomchristie/django-rest-framework/q/stackoverflow/16857450/how-to-register-users-in-django-rest-framework
class UserSerializer(serializers.ModelSerializer):
    analyzed_events = serializers.PrimaryKeyRelatedField(many=True, allow_null=True, queryset=AnalyzedEvent.objects.all())

    class Meta:
        model = User
        fields = ('id', 'username','password', 'email', 'first_name', 'last_name', 'analyzed_events')
        write_only_fields = ('password',)
        read_only_fields = ('id', 'is_staff', 'is_superuser', 'is_active', 'date_joined',)


    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )

        user.set_password(validated_data['password'])
        user.save()

        return user


class AnalyzedEventSerializer(serializers.ModelSerializer):

    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = AnalyzedEvent
        fields = ('id', 'title', 'created', 'owner', 'event_data', 'submitted')
