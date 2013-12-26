from rest_framework import serializers
from .models import Person, Party, Facebook_Status, Facebook_Feed


class PersonSerializer(serializers.HyperlinkedModelSerializer):
    party_name = serializers.Field(source='party.name')

    class Meta:
        model = Person
        fields = ('id', 'name', 'party', 'party_name', 'url')


class PartySerializer(serializers.ModelSerializer):
    persons = serializers.SlugRelatedField(many=True, slug_field='slug')

    class Meta:
        model = Party
        fields = ('id', 'name', 'persons')


class FacebookFeedSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Facebook_Feed
        fields = ('vendor_id', 'person')


class FacebookStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Facebook_Status
        fields = ('status_id', 'feed')