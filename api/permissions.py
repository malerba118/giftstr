from django.contrib.auth.models import AnonymousUser, User
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import permissions
from api.models import Person, Product, Share

__author__ = 'austin'

class IsNotAuthenticated(permissions.BasePermission):
    message = 'You are already logged in.'

    def has_permission(self, request, view):
        return request.user == AnonymousUser

class IsAuthenticatedAndIsOwner(permissions.BasePermission):
    message = "You are not the owner of this person."

    def has_permission(self, request, view):

        person = get_object_or_404(Person, pk=view.kwargs.get("pk", None))
        return request.user != AnonymousUser and person.user == request.user




class IsAuthenticatedAndIsSameUser(permissions.BasePermission):
    message = "You are not the owner of this person."

    def has_permission(self, request, view):

        user = get_object_or_404(User, pk=view.kwargs.get("pk", None))
        return request.user != AnonymousUser and user == request.user


class IsAuthenticatedAndIsShareOwner(permissions.BasePermission):
    message = "You are not the owner of this share."

    def has_permission(self, request, view):

        share = get_object_or_404(Share, pk=view.kwargs.get("pk", None))
        return request.user != AnonymousUser and share.person.user == request.user



class IsPermitted(permissions.BasePermission):
    message = "You are not allowed to view this person's likes."

    def has_permission(self, request, view):

        person = get_object_or_404(Person, pk=view.kwargs.get("pk", None))
        return person.permitted.filter(pk=request.user.pk).exists() or \
               person.user == request.user