import ast
import json
from django.contrib.auth.models import User
from api.models import Person, Product, Suggestion, Share
from rest_framework import serializers

__author__ = 'austin'


class DynamicFieldsSerializerMixin(object):
    """
    Used to add fields argument to serializers at point of instantiation.
    These are the fields to be returned on a GET request.
    Fields options include those specified under the serializer's meta class.
    """

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop('fields', None)

        # Instantiate the superclass normally
        super(DynamicFieldsSerializerMixin, self).__init__(*args, **kwargs)

        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class UserSerializer(DynamicFieldsSerializerMixin, serializers.HyperlinkedModelSerializer):

    password = serializers.CharField(
        style={'input_type': 'password'}, write_only=True
    )

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'password',
            'email',
            'first_name',
            'last_name'
        )


class PersonSerializer(DynamicFieldsSerializerMixin, serializers.HyperlinkedModelSerializer):

    user = UserSerializer(read_only=True)

    class Meta:
        model = Person
        fields = (
            'id',
            'user',
            'name',
        )
        read_only_fields = (
            'id',
            'user'
        )



class ProductSerializer(DynamicFieldsSerializerMixin, serializers.HyperlinkedModelSerializer):

    item = serializers.JSONField()

    class Meta:
        model = Product
        fields = (
            'id',
            'ASIN',
            'item',
        )
        read_only_fields = (
            "id",
            "ASIN",
            "item",
        )


class SuggestionSerializer(DynamicFieldsSerializerMixin, serializers.HyperlinkedModelSerializer):

    product = ProductSerializer(read_only = True)

    class Meta:
        model = Suggestion
        fields = (
            "id",
            "product",
            "relevance",
        )


class ShareSerializer(DynamicFieldsSerializerMixin, serializers.HyperlinkedModelSerializer):

    user = UserSerializer(read_only=True)
    person = PersonSerializer(read_only=True)

    class Meta:
        model = Share
        fields = (
            "id",
            "user",
            "person",
        )
        read_only_fields = (
            "id",
        )