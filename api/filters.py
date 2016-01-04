from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework.filters import BaseFilterBackend
from api.models import Person

__author__ = 'austin'


class UserFilterBackend(BaseFilterBackend):
    """
    Filter that only allows users to see their own objects.
    """
    def filter_queryset(self, request, queryset, view):
        person_pk = request.GET.get("personId", None)
        person = get_object_or_404(Person, pk=person_pk)
        #Users that are not yet permitted to view this person and are not the current user
        return queryset.filter(~Q(pk__in=person.permitted.all()) & ~Q(pk=request.user.pk))