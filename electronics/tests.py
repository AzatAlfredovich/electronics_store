from django.test import TestCase
from django.core.exceptions import ValidationError

from electronics.models import NetworkNode


class RetailNetworkHierarchyTest(TestCase):

    def test_cannot_reference_itself(self):
        """Объект не может быть поставщиком сам себе"""
        node = NetworkNode.objects.create(
            name='Test Factory',
            node_type="factory",
            hierarchy_level=0,
            email='factory@test.com',
            country='Russia',
            city='Moscow',
            street='Main',
            house_number='1'
        )

        node.supplier = node

        with self.assertRaises(ValidationError) as cm:
            node.full_clean()

        self.assertIn(
            "Звено сети не может ссылаться само на себя как на поставщика!",
            str(cm.exception)
        )

    def test_factory_cannot_have_supplier(self):
        """Завод не может иметь поставщика"""
        factory = NetworkNode.objects.create(
            name='Factory',
            node_type="factory",
            hierarchy_level=0,
            email='factory@test.com',
            country='USA',
            city='NY',
            street='Main',
            house_number='1'
        )

        store = NetworkNode.objects.create(
            name='Store',
            node_type="retail",
            hierarchy_level=1,
            email='store@test.com',
            country='USA',
            city='NY',
            street='Second',
            house_number='2'
        )

        factory.supplier = store

        with self.assertRaises(ValidationError) as cm:
            factory.full_clean()

        self.assertIn("Завод не может иметь поставщика!", str(cm.exception))

    def test_cannot_create_cycle_direct(self):
        """Нельзя создать прямой цикл (A -> A)"""
        node = NetworkNode.objects.create(
            name='Node A',
            node_type="retail",
            email='a@test.com',
            country='USA',
            city='NY',
            street='Street',
            house_number='1'
        )

        node.supplier = node

        with self.assertRaises(ValidationError) as cm:
            node.full_clean()

        self.assertIn("Звено сети не может ссылаться само на себя", str(cm.exception))

    def test_cannot_create_cycle_three_nodes(self):
        """Нельзя создать цикл из трёх узлов (A -> B -> C -> A)"""
        # Все узлы — не заводы, чтобы избежать правила «завод не может иметь поставщика»
        node_a = NetworkNode.objects.create(
            name='Node A',
            node_type="retail",
            email='a@test.com',
            country='USA',
            city='NY',
            street='Street',
            house_number='1'
        )

        node_b = NetworkNode.objects.create(
            name='Node B',
            node_type="retail",
            email='b@test.com',
            country='USA',
            city='NY',
            street='Second',
            house_number='2'
        )

        node_c = NetworkNode.objects.create(
            name='Node C',
            node_type="entrepreneur",
            email='c@test.com',
            country='USA',
            city='NY',
            street='Third',
            house_number='3'
        )

        # Создаём цепочку: A → B → C
        node_b.supplier = node_a
        node_c.supplier = node_b

        # Пытаемся создать цикл: C → A (замыкаем цепочку)
        node_a.supplier = node_c

        with self.assertRaises(ValidationError) as cm:
            node_a.save()  # Вызываем save(), а не full_clean()

        self.assertIn("Обнаружена циклическая ссылка", str(cm.exception))

    def test_hierarchy_level_calculation_simple(self):
        """Проверка расчёта уровня иерархии для простой цепочки"""
        factory = NetworkNode.objects.create(
            name='Factory',
            node_type="factory",
            email='factory@test.com',
            country='USA',
            city='NY',
            street='Main',
            house_number='1'
        )

        store = NetworkNode.objects.create(
            name='Store',
            node_type="retail",
            email='store@test.com',
            country='USA',
            city='NY',
            street='Second',
            house_number='2',
            supplier=factory
        )

        entrepreneur = NetworkNode.objects.create(
            name='IP',
            node_type="entrepreneur",
            email='ip@test.com',
            country='USA',
            city='NY',
            street='Third',
            house_number='3',
            supplier=store
        )

        # Перезагружаем объекты, чтобы убедиться, что hierarchy_level рассчитан
        factory.refresh_from_db()
        store.refresh_from_db()
        entrepreneur.refresh_from_db()

        self.assertEqual(factory.hierarchy_level, 0)
        self.assertEqual(store.hierarchy_level, 1)
        self.assertEqual(entrepreneur.hierarchy_level, 2)

    def test_hierarchy_level_update_on_supplier_change(self):
        """Проверка пересчёта уровня иерархии при изменении поставщика"""
        factory1 = NetworkNode.objects.create(
            name='Factory 1',
            node_type="factory",
            email='f1@test.com',
            country='USA',
            city='NY',
            street='Main',
            house_number='1'
        )

        factory2 = NetworkNode.objects.create(
            name='Factory 2',
            node_type="factory",
            email='f2@test.com',
            country='USA',
            city='LA',
            street='Main',
            house_number='2'
        )

        store = NetworkNode.objects.create(
            name='Store',
            node_type="retail",
            email='store@test.com',
            country='USA',
            city='NY',
            street='Second',
            house_number='2',
            supplier=factory1
        )

        # Меняем поставщика
        store.supplier = factory2
        store.save()

        store.refresh_from_db()
        self.assertEqual(store.hierarchy_level, 1)

    def test_valid_hierarchy_creation(self):
        """Создание валидной иерархии без ошибок"""
        factory = NetworkNode.objects.create(
            name='Factory',
            node_type="factory",
            email='factory@test.com',
            country='USA',
            city='NY',
            street='Main',
            house_number='1'
        )

        store = NetworkNode.objects.create(
            name='Store',
            node_type="retail",
            email='store@test.com',
            country='USA',
            city='NY',
            street='Second',
            house_number='2',
            supplier=factory
        )

        # Валидация должна пройти успешно
        store.full_clean()
        self.assertEqual(store.hierarchy_level, 1)