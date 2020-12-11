from rest_framework import permissions
from rmmapi.models import Rater

class MustBeCreatorToModify(permissions.IsAuthenticated):
    """Object level permission that only allows creators of an object to modify them."""

    message = 'You must be the creator of this object to modify it.'

    def has_object_permission(self, request, view, creator):
        if request.method == 'DELETE' or request.method == 'PUT':
            rater = Rater.objects.get(user=request.auth.user)
            return creator == rater
        return True
