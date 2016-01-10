from django.contrib.auth.models import User
from django.core.serializers import json
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404

# Create your views here.
from django_filters import filters
from rest_framework import status
from rest_framework.filters import SearchFilter
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from api.filters import UserFilterBackend
from api.models import Person, PersonSimilarity, Product, Suggestion, Share
from permissions import IsNotAuthenticated, IsAuthenticatedAndIsOwner, IsAuthenticatedAndIsSameUser, \
    IsAuthenticatedAndIsShareOwner, IsPermitted
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from serializers import UserSerializer, PersonSerializer, ProductSerializer, SuggestionSerializer, ShareSerializer
from rest_framework.generics import ListCreateAPIView, RetrieveAPIView, ListAPIView, CreateAPIView, \
    RetrieveDestroyAPIView, DestroyAPIView
from allauth.socialaccount.providers.amazon.views import AmazonOAuth2Adapter
from rest_auth.registration.views import SocialLoginView
from gift_finder import settings


class DynamicFieldsViewMixin(object):


     def get_serializer(self, *args, **kwargs):
        """
        Define get_serializer method to include context and fields keywords
        to support a fields query parameter.
        """
        serializer_class = self.get_serializer_class()

        fields = None
        if self.request.method == 'GET':
            query_fields = self.request.query_params.get("fields", None)

            if query_fields:
                fields = tuple(query_fields.split(','))


        kwargs['context'] = self.get_serializer_context()
        kwargs['fields'] = fields

        return serializer_class(*args, **kwargs)


class AmazonLogin(SocialLoginView):
    adapter_class = AmazonOAuth2Adapter

class UserList(DynamicFieldsViewMixin, ListAPIView):
    """
    GET: List of users, searchable by username and by those
    who havent been shared with a given person
    """
    queryset = User.objects.all().order_by("username")
    serializer_class = UserSerializer
    filter_backends = (SearchFilter, UserFilterBackend,)
    search_fields = ('username',)


class CurrentUserDetailView(RetrieveDestroyAPIView):

    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user



class PersonList(DynamicFieldsViewMixin, ListCreateAPIView):
    """
    GET: List of current user's persons
    POST: Create a new person for current user
    """
    serializer_class = PersonSerializer

    def get_queryset(self):
        user = self.request.user
        return Person.objects.filter(user=user)


    def create(self, request, *args, **kwargs):

        name = request.POST.get('name', None)

        #Ughh so hacky, need to fix this. Damn serializer read_only_fields seem buggy, they claim to be required for POSTs.
        #Overriding perform_create worked in django 1.8 but seems to fail in 1.9 claiming read only fields are required for writes.
        if (name in [None, 'undefined', ''] or Person.objects.filter(name=name, user=request.user).exists()):
            response = Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            new_person = Person.objects.create(name=name, user=request.user)

            for p2 in Person.objects.all():
                PersonSimilarity.objects.get_or_create(person1=new_person, person2=p2, similarity=0)
                PersonSimilarity.objects.get_or_create(person1=p2, person2=new_person, similarity=0)

            for product in [p for p in Product.objects.filter(ASIN__in=settings.DEFAULT_SUGGESTIONS)]:
                Suggestion.objects.get_or_create(person=new_person, product=product, relevance = .99)

            serializer = PersonSerializer(new_person)
            response = JsonResponse(serializer.data)

        return response

    # def perform_create(self, serializer):
    #     new_person = serializer.save(user=self.request.user)
    #
    #     for p2 in Person.objects.all():
    #         PersonSimilarity.objects.get_or_create(person1=new_person, person2=p2, similarity=0)
    #         PersonSimilarity.objects.get_or_create(person1=p2, person2=new_person, similarity=0)
    #
    #     for product in [p for p in Product.objects.filter(ASIN__in=settings.DEFAULT_SUGGESTIONS)]:
    #         Suggestion.objects.get_or_create(person=new_person, product=product, relevance=.99)





class SuggestionList(DynamicFieldsViewMixin, ListAPIView):
    """
    GET: List of all suggestions
    """
    serializer_class = SuggestionSerializer
    permission_classes = (IsAuthenticatedAndIsOwner,)

    def get_queryset(self):
        person = get_object_or_404(Person, pk=self.kwargs.get("pk", None))

        suggestions = Suggestion.objects.filter(person = person).order_by("-relevance")

        if suggestions.count() == 0 or person.likes_until_refresh <= 0: #triggers for suggestion refresh
            person.update_person_similarities() #recalculate most similar persons
            person.update_product_suggestions()
            suggestions = Suggestion.objects.filter(person = person).order_by("-relevance")
            person.likes_until_refresh = settings.LIKES_UNTIL_REFRESH
            person.save()

        return suggestions


class LikeList(DynamicFieldsViewMixin, ListCreateAPIView):
    """
    GET: List of all likes for person
    POST: Like a new product
    """
    serializer_class = ProductSerializer
    permission_classes = [IsPermitted]

    def get_queryset(self):
        person_pk = self.kwargs.get("pk", None)
        person = get_object_or_404(Person, pk=person_pk)
        return person.likes.all().order_by("ASIN")

    def create(self, request, *args, **kwargs):
        person_pk = kwargs.get("pk", None)
        person = get_object_or_404(Person, pk=person_pk)
        product_pk = request.POST.get("productId", None)
        product = get_object_or_404(Product, pk=product_pk)

        #delete suggestion
        suggestion = Suggestion.objects.filter(person=person, product=product)
        suggestion.delete()

        #like product
        person.likes.add(product)
        person.likes_until_refresh -= 1

        #mark product as seen
        person.seen.add(product)

        person.save()

        return HttpResponse("Success")


class SkipCreateView(DynamicFieldsViewMixin, CreateAPIView):
    """
    POST: "Dislike" a product
    """
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedAndIsOwner]


    def create(self, request, *args, **kwargs):
        person_pk = kwargs.get("pk", None)
        person = get_object_or_404(Person, pk=person_pk)
        product_pk = request.POST.get("productId", None)
        product = get_object_or_404(Product, pk=product_pk)

        #delete suggestion
        suggestion = Suggestion.objects.filter(person=person, product=product)
        suggestion.delete()

        #mark product as seen
        person.seen.add(product)

        return HttpResponse("Success")


class PersonDetailView(DynamicFieldsViewMixin, RetrieveDestroyAPIView):
    lookup_field = 'pk'
    url_kwarg = 'pk'
    queryset = Person.objects.all()
    serializer_class = PersonSerializer
    permission_classes = [IsAuthenticatedAndIsOwner]


class SharePersonListView(DynamicFieldsViewMixin, ListCreateAPIView):

    serializer_class = ShareSerializer
    permission_classes = [IsAuthenticatedAndIsOwner]

    def get_queryset(self):
        person_pk = self.kwargs.get("pk", None)
        person = get_object_or_404(Person, pk=person_pk)
        return Share.objects.filter(person=person).order_by("-timestamp")

    def create(self, request, *args, **kwargs):
        person_pk = kwargs.get("pk", None)
        person = get_object_or_404(Person, pk=person_pk)
        user_pk = request.POST.get("userId", None)
        user = get_object_or_404(User, pk=user_pk)
        if not Share.objects.filter(user=user, person=person).exists():
            share = Share.objects.create(user=user, person=person)
            serializer = ShareSerializer(share)
            response = JsonResponse(serializer.data)
        else:
            response = Response("Share already exists", status=409)
        return response

class ShareDeleteView(DynamicFieldsViewMixin, DestroyAPIView):

    serializer_class = ShareSerializer
    permission_classes = [IsAuthenticatedAndIsShareOwner]

    def destroy(self, request, *args, **kwargs):
        share_pk = kwargs.get("pk", None)
        share = get_object_or_404(Share, pk=share_pk)
        share.delete()
        return HttpResponse("Success", status=200)


class ShareUserListView(DynamicFieldsViewMixin, ListAPIView):

    serializer_class = ShareSerializer

    def get_queryset(self):
        return Share.objects.filter(user=self.request.user).order_by("-timestamp")
