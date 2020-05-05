from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the snippet.
        return obj.owner == request.user

#class IsStaffOrTargetUserUpdateOnly(permissions.BasePermission):
#    """
#    Custom permission to only allow the user or staff to edit the user's information.
#    """
#
#    #def has_permission(self, request, view):
#    #    # allow user to update all users if logged in user is staff
#    #    return view.action == 'update' or request.user.is_staff
#
#    def has_object_permission(self, request, view, obj):
#        # allow logged in user to update own details, allows staff to update all records
#        return request.user.is_staff or obj == request.user


# https://richardtier.com/2014/02/25/django-rest-framework-user-endpoint/

class IsStaffOrTargetUser(permissions.BasePermission):
    def has_permission(self, request, view):
        # allow user to list all users if logged in user is staff
        return view.action == 'retrieve' or request.user.is_staff

    def has_object_permission(self, request, view, obj):
        # allow logged in user to view own details, allows staff to view all records
        return request.user.is_staff or obj == request.user

class IsLocalStaffOrTargetUser(permissions.BasePermission):
    def has_permission(self, request, view):
        # allow user to list all users if logged in user is staff
        return view.action == 'retrieve' or request.user.is_staff

    def has_object_permission(self, request, view, obj):
        # allow logged in user to view own details, allows staff to view all records
        return (request.user.is_staff and (request.user.profile.institution == obj.profile.institution)) or obj == request.user


class IsLocalStaffOrOwner(permissions.BasePermission):
    """
    allow logged in user to view own details, allows staff for a given institution to view all user records for that institution
    """
    def has_object_permission(self, request, view, obj):
        return (request.user.is_staff and (request.user.profile.institution == obj.profile.institution)) or obj == request.user


class IsLocalStaffOrOwnerTheseEvents(permissions.BasePermission):
    """
    allow logged in user to view own events, allows staff for a given institution to view all user events for that institution
    """
    def has_object_permission(self, request, view, obj):
        #print(obj)
        return (request.user.is_staff and (request.user.profile.institution == obj.owner.profile.institution)) or obj.owner == request.user

    
