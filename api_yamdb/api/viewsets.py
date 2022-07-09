from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin,
                                   ListModelMixin)
from rest_framework.viewsets import GenericViewSet


class CreateListViewset(CreateModelMixin, DestroyModelMixin, ListModelMixin,
                        GenericViewSet):
    """Class CreateListViewset limits operations.
    By creating, destroying object and getting list of objects.
    """
    pass
