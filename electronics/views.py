from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.viewsets import ModelViewSet

from electronics.models import NetworkNode
from electronics.permissions import IsActiveAndStaffPermission
from electronics.serializers import NetworkNodeSerializer


class NetworkNodeViewSet(ModelViewSet):
    """CRUD-вьюсеты для звеньев сети"""

    queryset = NetworkNode.objects.select_related("supplier").prefetch_related(
        "products"
    )
    serializer_class = NetworkNodeSerializer

    # Доступ только для активных сотрудников
    permission_classes = [IsActiveAndStaffPermission]

    # Подключаем фильтрацию, поиск и сортировку
    filter_backends = [
        DjangoFilterBackend,  # фильтрация по точным значениям полей
        SearchFilter,  # поиск по текстовым полям
        OrderingFilter,  # сортировка по указанным полям
    ]

    # Фильтрация по стране
    filterset_fields = ("country",)

    # Поля, по которым будет работать поиск ?search=
    search_fields = (
        "name",
        "city",
        "country",
        "email",
    )

    # Поля, по которым можно сортировать через ?ordering=
    ordering_fields = (
        "name",
        "created_at",
        "country",
        "city",
        "hierarchy_level",
    )

    # Сортировка по умолчанию
    ordering = ("name",)
