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
                  'computed_name', 'computed_human_readable_name')

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
        print('validated data: ', validated_data)
        inst_id = validated_data["profile"]["institution"]["id"]
        print('institution id: ', inst_id)

        
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

    # https://stackoverflow.com/questions/39755669/overriding-update-django-rest-framework
    def update(self, instance, validated_data):

    # for updating the password, try: https://stackoverflow.com/questions/38845051/how-to-update-user-password-in-django-rest-framework
    # ...but might first watch these videos:
        # - making sure only a logged-out user can reset their password: https://www.youtube.com/watch?v=e4ccNsrF7YI
        # - generate password reset email: https://www.youtube.com/watch?v=VLOM-mZCfpk
        # - next part: https://www.youtube.com/watch?v=K-qHzxrNtoI

        print('instance: ', instance)
        print('validated data: ', validated_data)

        # https://thinkster.io/tutorials/django-json-api/authentication
        password = validated_data.pop('password', None)
        profile = validated_data.pop('profile', None)

        for (key, value) in validated_data.items():
            # For the keys remaining in `validated_data`, we will set them on
            # the current `User` instance one at a time.
            setattr(instance, key, value)

        if password is not None:
            # `.set_password()`  handles all
            # of the security stuff that we shouldn't be concerned with.
            instance.set_password(password)

        # don't do anything to the events

        instance.save()

        if profile is not None:
            inst_id = profile['institution']['id']
            print('updating institution: ', inst_id)
            self.update_or_create_profile(instance, inst_id)

        return instance



    def update_or_create_profile(self, user, inst_id):
        # This always creates a Profile if the User is missing one
        # Need to fetch the institution for the given id first....
        # TODO: catch exception if the institution does not exist, and then throw an http error:
        #       - error is: DoesNotExist: Institution matching query does not exist.
        #       - see: http://www.django-rest-framework.org/api-guide/exceptions/
        #       - Note: looked into this a bit, but not sure that it's worth it; an
        #         exception does get thrown automatically at the moment, and the
        #         user gets an "Internal Server Error" message.  That's not very helpful,
        #         but if the institution does not exist in the db, then the user
        #         can't do anything about it anyways....

        # https://stackoverflow.com/questions/31418714/update-or-create-wont-respect-unique-key
        institution = Institution.objects.get(pk = inst_id)
        Profile.objects.update_or_create(user=user, defaults={'institution': institution})


class AnalyzedEventSerializer(serializers.ModelSerializer):

    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = AnalyzedEvent
        fields = ('id', 'title', 'created', 'updated', 'owner', 'event_data', 'submitted')


class InstitutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Institution
        fields = ('id','name')
