import uuid

from django.db import IntegrityError
from django.db.models import Avg
from rest_framework.decorators import action, api_view
from rest_framework.filters import SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken

from api.filters import TitleFilter
from api.permissions import IsAdmin, IsAdminModeratorAuthorOrReadOnly, ReadOnly
from api.serializers import (CategorySerializer, CommentSerializer,
                             GenreSerializer, ProfileSerializer,
                             ReviewSerializer, SignUpSerializer,
                             TitleReadSerializer, TitleWriteSerializer,
                             TokenSerializer, UserSerializer)
from api.utils import send_confirmation_code
from api.viewsets import CreateListViewset
from reviews.models import Category, Genre, Review, Title, User


@api_view(['POST'])
def signup_view(request):
    """Create user with unique username and email.
    Send confirmation code to user email.
    """
    serializer = SignUpSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.validated_data['email']
    username = serializer.validated_data['username']
    try:
        user, create = User.objects.get_or_create(
            username=username,
            email=email
        )
    except IntegrityError:
        return Response(
            'username или email уже существуют!',
            status=HTTP_400_BAD_REQUEST
        )
    confirmation_code = str(uuid.uuid4())
    user.confirmation_code = confirmation_code
    user.save()
    send_confirmation_code(user)
    return Response(serializer.data, status=HTTP_200_OK)


@api_view(['POST'])
def token_view(request):
    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data['username']
    user = get_object_or_404(User, username=username)
    confirmation_code = serializer.validated_data['confirmation_code']
    uuid_code = user.confirmation_code
    if uuid_code != confirmation_code:
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
    refresh = RefreshToken.for_user(user)
    return Response({'access': str(refresh.access_token)}, status=HTTP_200_OK)


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdmin, )
    ordering = ('username', )
    filter_backends = (SearchFilter, )
    pagination_class = PageNumberPagination
    lookup_field = 'username'
    lookup_value_regex = r'[\w\@\.\+\-]+'
    search_fields = ('username', )

    @action(
        detail=False, methods=['get', 'patch'],
        url_path='me', url_name='me',
        permission_classes=(IsAuthenticated, )
    )
    def about_me(self, request):
        serializer = ProfileSerializer(request.user)
        if request.method == 'PATCH':
            serializer = ProfileSerializer(
                request.user, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
        return Response(serializer.data, status=HTTP_200_OK)


class CategoryViewSet(CreateListViewset):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdmin | ReadOnly, )
    filter_backends = (SearchFilter, )
    lookup_field = 'slug'
    search_fields = ('=name', )
    ordering = ('name', )


class GenreViewSet(CreateListViewset):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdmin | ReadOnly, )
    filter_backends = (SearchFilter, )
    lookup_field = 'slug'
    search_fields = ('=name', )
    ordering = ('name', )


class TitleViewSet(ModelViewSet):

    queryset = Title.objects.all().annotate(
        Avg('reviews__score')).order_by('name')

    permission_classes = (IsAdmin | ReadOnly, )
    filterset_class = TitleFilter
    ordering = ('name', )

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleReadSerializer
        return TitleWriteSerializer


class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (IsAdminModeratorAuthorOrReadOnly, )

    def get_queryset(self):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        return title.reviews.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAdminModeratorAuthorOrReadOnly, )

    def get_queryset(self):
        review = get_object_or_404(Review, pk=self.kwargs.get('review_id'))
        return review.comments.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, id=review_id, title=title_id)
        serializer.save(author=self.request.user, review=review)
