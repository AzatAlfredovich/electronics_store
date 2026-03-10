from rest_framework import serializers

from electronics.models import NetworkNode, Product


class ProductSerializer(serializers.ModelSerializer):
    """Сериализатор для продукта."""

    class Meta:
        model = Product
        fields = ("id", "name", "model", "release_date")


class NetworkNodeSerializer(serializers.ModelSerializer):
    """Сериализатор для звена сети."""

    # Показываем продукты только для чтения (связанные товары)
    products = ProductSerializer(many=True, read_only=True)

    # Отдельное поле для записи продуктов по их id
    product_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Product.objects.all(),
        source="products",
        write_only=True,
        required=False,
    )

    class Meta:
        model = NetworkNode
        fields = (
            "id",
            "name",
            "node_type",
            "email",
            "country",
            "city",
            "street",
            "house_number",
            "supplier",
            "products",
            "product_ids",
            "debt_to_supplier",
            "hierarchy_level",
            "created_at",
        )

        # Поля только для чтения
        read_only_fields = (
            "debt_to_supplier",  # запрещено обновлять
            "hierarchy_level",  # считается автоматически
            "created_at",  # заполняется автоматически
        )
