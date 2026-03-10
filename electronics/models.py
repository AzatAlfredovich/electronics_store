from django.core.exceptions import ValidationError
from django.db import models


class Product(models.Model):
    """Модель продукта электроники"""

    # Название продукта
    name = models.CharField(
        max_length=100,
        verbose_name="Название",
    )

    # Модель продукта
    model = models.CharField(
        max_length=100,
        verbose_name="Модель",
    )

    # Дата выхода продукта на рынок
    release_date = models.DateField(
        verbose_name="Дата выхода на рынок",
    )

    class Meta:
        verbose_name = "продукт"
        verbose_name_plural = "продукты"
        ordering = ("name", "model")

    def __str__(self):
        """Строковое отображение продукта"""
        return f"{self.name} ({self.model})"


class NetworkNode(models.Model):
    """Модель звена сети по продаже электроники"""

    class NodeType(models.TextChoices):
        # Тип звена отдельно от уровня иерархии
        FACTORY = "factory", "Завод"
        RETAIL = "retail", "Розничная сеть"
        ENTREPRENEUR = "entrepreneur", "Индивидуальный предприниматель"

    # Название звена сети
    name = models.CharField(
        max_length=100,
        verbose_name="Название",
    )

    # Тип звена: завод/розничная сеть/ИП
    node_type = models.CharField(
        max_length=30,
        choices=NodeType.choices,
        verbose_name="Тип звена",
    )

    # Контактные данные
    email = models.EmailField(
        verbose_name="Email",
    )
    country = models.CharField(
        max_length=50,
        verbose_name="Страна",
    )
    city = models.CharField(
        max_length=50,
        verbose_name="Город",
    )
    street = models.CharField(
        max_length=100,
        verbose_name="Улица",
    )
    house_number = models.CharField(
        max_length=10,
        verbose_name="Номер дома",
    )

    # Поставщик (ссылка на другое звено этой же сети)
    supplier = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,              # null=True/blank=True у завода поставщика нет
        blank=True,
        related_name="clients",
        verbose_name="Поставщик",
    )

    # У одного звена может быть несколько продуктов,
    # и один продукт может продаваться в разных звеньях сети
    products = models.ManyToManyField(
        Product,
        blank=True,
        related_name="network_nodes",
        verbose_name="Продукты",
    )

    # Задолженность перед поставщиком
    debt_to_supplier = models.DecimalField(
        max_digits=12,           #2 знака после запятой
        decimal_places=2,
        default=0,
        verbose_name="Задолженность перед поставщиком",
    )

    # Уровень иерархии считаем автоматически
    hierarchy_level = models.PositiveSmallIntegerField(
        default=0,
        editable=False,           # editable=False скрывает поле из обычного редактирования
        verbose_name="Уровень иерархии",
    )

    # Дата и время создания объекта
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Время создания",
    )

    class Meta:
        verbose_name = "звено сети"
        verbose_name_plural = "звенья сети"
        ordering = ("name",)

    def __str__(self):
        """Строковое отображение объекта"""
        return self.name

    def clean(self):
        """Проверка бизнес-логики модели перед сохранением"""

        # Запрещаем ссылку объекта на самого себя
        if self.supplier and self.supplier == self:
            raise ValidationError(
                "Звено сети не может ссылаться само на себя как на поставщика!"
            )

        # По условию завод верхний уровень, поэтому поставщика у него быть не должно
        if self.node_type == self.NodeType.FACTORY and self.supplier is not None:
            raise ValidationError("Завод не может иметь поставщика!")

    def calculate_hierarchy_level(self):
        """Вычисляет уровень иерархии по цепочке поставщиков"""
        level = 0
        supplier = self.supplier

        # Множество нужно для защиты от циклических ссылок: например A -> B -> C -> A
        visited_ids = set()

        while supplier is not None:
            # Если поставщик уже встречался, значит есть цикл
            if supplier.pk in visited_ids:
                raise ValidationError(
                    "Обнаружена циклическая ссылка"
                )

            visited_ids.add(supplier.pk)
            level += 1
            supplier = supplier.supplier

        return level

    def save(self, *args, **kwargs):
        """Сохраняет объект с предварительной валидацией и расчетом уровня"""

        # full_clean запускает clean() и встроенные проверки полей модели
        self.full_clean()

        # Перед сохранением автоматически пересчитываем уровень
        self.hierarchy_level = self.calculate_hierarchy_level()

        super().save(*args, **kwargs)
