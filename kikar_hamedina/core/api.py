# from django.http import Http404
# from django.views.generic import View
# from rest_framework import status
# from rest_framework.decorators import api_view
# from rest_framework.views import APIView, View
# from rest_framework.response import Response
# from rest_framework import generics
# from rest_framework import mixins
# from rest_framework import permissions
# from rest_framework import filters
# from rest_framework.reverse import reverse
# from .serializers import PersonSerializer, PartySerializer, FacebookStatusSerializer, FacebookFeedSerializer
# from .models import Facebook_Status, Facebook_Feed
# from persons.models import Person, Party
#
# class PersonsList(generics.ListAPIView):
#     queryset = Person.objects.all()
#     serializer_class = PersonSerializer
#
#
# class PersonDetail(generics.RetrieveAPIView):
#     queryset = Person.objects.all()
#     serializer_class = PersonSerializer
#
#
# class StatusList(generics.ListAPIView):
#     queryset = Facebook_Status.objects.all()
#     serializer_class = FacebookStatusSerializer
#     filter_backends = (filters.DjangoFilterBackend,)
#     filter_fields = ('id', 'like_count', 'feed')
#
#
# class FeedList(generics.ListAPIView):
#     queryset = Facebook_Feed.objects.all()
#     serializer_class = FacebookFeedSerializer
#
#
# class PartyDetail(generics.RetrieveAPIView):
#     queryset = Party.objects.select_related()
#     serializer_class = PartySerializer
#
#
# class PartiesList(generics.ListAPIView):
#     queryset = Party.objects.all()
#     serializer_class = PartySerializer
#     permission_classes = [
#         permissions.AllowAny
#     ]