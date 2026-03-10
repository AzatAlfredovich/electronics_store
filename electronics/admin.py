from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.db.models import QuerySet  # набор объектов из базы данных
from django.http import HttpRequest  # тип HTTP-запроса
from django.urls import reverse  # URL по имени маршрута
from django.utils.html import format_html  # вывести HTML в Django

from electronics.models import NetworkNode, Product


@admin.register(Product)
class ProductAdmin(ModelAdmin):
    """Настройки админки для продуктов"""

    # Какие поля показывать в списке объектов
    list_display = ("id", "name", "model", "release_date")

    # По каким полям работает поиск
    search_fields = ("name", "model")


@admin.register(NetworkNode)
class NetworkNodeAdmin(ModelAdmin):
    """Настройки админки для звеньев сети"""

    # Поля, которые будут видны в таблице админки
    list_display = (
        "id",
        "name",
        "node_type",
        "supplier_link",  # ссылка на поставщика
        "city",
        "country",
        "debt_to_supplier",
        "hierarchy_level",
        "created_at",
    )

    # Фильтры
    list_filter = ("city", "country", "node_type")

    # Поиск по полям
    search_fields = ("name", "email", "city", "country")

    # Поля для чтения
    readonly_fields = ("hierarchy_level", "created_at")

    # Action в выпадающий список "Действие"
    actions = ("clear_debt_to_supplier",)

    def supplier_link(self, obj: NetworkNode) -> str:
        """
        Делаем поставщика кликабельной ссылкой в админке
        """
        # У завода поставщика нет
        if obj.supplier is None:
            return "-"

        # Формируем ссылку на страницу редактирования поставщика в админке
        url = reverse(
            "admin:electronics_networknode_change",
            args=[obj.supplier.pk],
        )

        # format_html безопасно формирует HTML для Django admin
        return format_html('<a href="{}">{}</a>', url, obj.supplier.name)

    # Колонка в админке
    supplier_link.short_description = "Поставщик"

    @admin.action(description="Очистить задолженность перед поставщиком")
    def clear_debt_to_supplier(
        self,
        request: HttpRequest,
        queryset: QuerySet[NetworkNode],
    ) -> None:
        """
        Обнуляет задолженность у выбранных звеньев сети
        """
        # Массово обновляем поле у выбранных объектов
        queryset.update(debt_to_supplier=0)
