from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.db.models import Prefetch, Count
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from itertools import chain
from rest_framework.decorators import list_route
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, permissions, viewsets
from rest_framework import generics

from serializers import ReviewSerializer, ReviewsSerializer, CategorySerializer, PlacesSerializer
from .models import Place, Review, Category, InterestedPeople
from friends.models import Friend

User = get_user_model()

class PlaceListView(generics.ListAPIView):
    serializer_class = PlacesSerializer
    authentication_classes = (TokenAuthentication, SessionAuthentication)

    def get_queryset(self):
        """
        Get places where a friends put a review
        """

        friends = Friend.objects.friends(self.request.user)
        all_friends = list(friends)

        for friend in friends:
            friend_friends = Friend.objects.friends(friend)
            all_friends = list(chain(all_friends, friend_friends))

        all_friends.append(self.request.user)

        friends_reviews = Review.objects.filter(created_by__in=all_friends)

        queryset = Place.objects.filter(
            reviews__in=friends_reviews
        ).prefetch_related(
            Prefetch(
                'reviews',
                queryset=Review.objects.filter(created_by__in=all_friends)
            )
        ).distinct()

        return queryset

class CategoryViewSet(viewsets.ViewSet):
    """
        Category View Set
    """

    #Manage the permission to the view set, only when authenticated
    permission_classes = (permissions.IsAuthenticated,)
    # two kind of authentication, token to be easier for test
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    serializer_class = CategorySerializer

    def list (self, request):
        queryset = Category.objects.all()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)


class ReviewViewSet(viewsets.ViewSet):
    """
    Review View Set
    """
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    serializer_class = ReviewSerializer
    serializer_class_list = ReviewSerializer

    def list(self, request):
        if request.user.is_authenticated():
            queryset = Review.objects.filter(created_by = request.user)
        else:
            queryset = Review.objects.all()

        serializer = self.serializer_class(queryset, many=True, context={'request':request})
        return Response(serializer.data)

    def create(self, request):
        serializer = self.serializer_class(data = request.data, context={'request':request})
        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data, status=status.HTTP_201_CREATED
            )

        return Response({
            'status': 'Bad request',
            'message': 'Review could not be created with received data.',
            'data': str(request.data),
            'validated_data': serializer.validated_data,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        queryset = Review.objects.all()
        myreview = get_object_or_404(queryset, pk = pk)

        serializer = ReviewSerializer(myreview)
        return Response(serializer.data)


    def update(self, request, pk=None):
        try:
            review = Review.objects.get(pk=pk)
        except Review.DoesNotExist:
            return Response({
                'status': 'Not Found',
                'message': 'Review could not be find.'
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(review, data = request.data, context={'request':request})
        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data, status=status.HTTP_202_ACCEPTED
            )

        return Response({
            'status': 'Bad request',
            'message': 'Review could not be created with received data.',
            'data': str(request.data),
            'validated_data': serializer.validated_data,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        pass

    def destroy(self, request, pk=None):
        try:
            review = Review.objects.get(pk=pk, created_by=request.user)
            review.delete()
        except Review.DoesNotExist:
            return Response({
                'status': 'Not Found',
                'message': 'Bookmark could not be find.'
            }, status=HTTP_404_NOT_FOUND)

        return Response({
            'status': 'Success',
            'message': 'Bookmark deleted'
        }, status=status.HTTP_200_OK)

class NotifyMe(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(NotifyMe, self).dispatch(request, *args, **kwargs)

    def post(self, request):
        email = request.POST.get("email", "")
        newInterested, _ = InterestedPeople.objects.get_or_create(email=email)
        return JsonResponse({email: email})
