from rest_framework import serializers
from decays.models import DecayType, AnalyzedEvent, Institution, Profile
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
    # analyzed_events ends up becoming a list of ids for the user's events
    analyzed_events = serializers.PrimaryKeyRelatedField(many=True, allow_null=True, queryset=AnalyzedEvent.objects.all())
    # maybe this: https://stackoverflow.com/questions/18517438/django-rest-framework-make-onetoone-relation-ship-feel-like-it-is-one-model
    institution_id = serializers.IntegerField(source='profile.institution.id', allow_null=True)
  
    class Meta:
        model = User
        fields = ('id', 'username','password', 'email', 'first_name', 'last_name', 'analyzed_events', 'institution_id', 'date_joined', 'is_staff')
        write_only_fields = ('password',)
        read_only_fields = ('id', 'is_staff', 'is_superuser', 'is_active', 'date_joined',)

# NOTE: create works (it creates a new user, as well as a profile for that user); update does not work;
#       probably need to overwrite the update method so that it gets the profile object and assigns that
#       properly, or something

    def create(self, validated_data):
        # I don't quite see how this works; the client only sends over an institution_id, but the validated_data object includes
        # a profile object with an institution object that has an id.  Somehow the institution_id line above must set things
        # up so that there is an entire profile object...?
        print 'validated data: ', validated_data
        inst_id = validated_data["profile"]["institution"]["id"]
        print 'institution id: ', inst_id

        
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
    
        user.set_password(validated_data['password'])
        
        user.save()
        self.update_or_create_profile(user, inst_id)

        return user


    def update_or_create_profile(self, user, inst_id):
        # This always creates a Profile if the User is missing one
        # Need to fetch the institution for the given id first....
        # TODO: catch exception if the institution does not exist, and then throw an http error:
        #       - error is: DoesNotExist: Institution matching query does not exist.
        #       - see: http://www.django-rest-framework.org/api-guide/exceptions/
        institution = Institution.objects.get(pk = inst_id)
        Profile.objects.update_or_create(user=user, institution = institution)

class AnalyzedEventSerializer(serializers.ModelSerializer):

    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = AnalyzedEvent
        fields = ('id', 'title', 'created', 'owner', 'event_data', 'submitted')


class InstitutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Institution
        fields = ('id','name')
