# shopapp/tests.py

from django.test import TestCase
from django.conf import settings
from django.urls import reverse
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from .models import Product, Order
from decimal import Decimal

class ProductCreateTestCase(TestCase):
    def setUp(self):
        # 1. Создаём пользователя
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

        # 2. Даём пользователю право add_product
        content_type = ContentType.objects.get_for_model(Product)
        permission = Permission.objects.get(
            codename='add_product',
            content_type=content_type
        )
        self.user.user_permissions.add(permission)

        # 3. Логинимся
        self.client.login(username='testuser', password='testpass123')

    def test_create_product(self):
        product_data = {
            "name": "Test Product",
            "price": 9.99,
            "description": "This is a test product.",
            "discount": 10,
        }

        response = self.client.post(
            reverse('shopapp:create_product'),
            data=product_data
        )

        # Проверяем редирект на список товаров
        self.assertRedirects(response, reverse('shopapp:products_list'))

        # Проверяем, что продукт создался
        product = Product.objects.get(name="Test Product")
        self.assertEqual(product.price, Decimal('9.99'))
        self.assertEqual(product.discount, 10)
        self.assertEqual(product.created_by, self.user)  # ← проверяем автора

    def test_create_product_no_permission(self):
        # Создаём пользователя без прав
        user_no_perm = User.objects.create_user(
            username='noperm',
            password='testpass123'
        )
        self.client.login(username='noperm', password='testpass123')

        product_data = {
            "name": "Test Product 2",
            "price": 19.99,
        }

        response = self.client.post(
            reverse('shopapp:create_product'),
            data=product_data
        )

        # Проверяем, что доступ запрещён (403)
        self.assertEqual(response.status_code, 403)

class ProductDetailsViewTestCase(TestCase):
    """Тесты для детальной страницы продукта"""

    def setUp(self):
        """Создаём продукт перед каждым тестом"""
        self.product = Product.objects.create(
            name="Test Product",
            price=9.99,
            description="Test description"
        )

    def tearDown(self):
        """Удаляем продукт после каждого теста"""
        self.product.delete()

    def test_get_product(self):
        """Тест: страница деталей продукта открывается"""
        response = self.client.get(
            reverse("shopapp:product_details", kwargs={"pk": self.product.pk})
        )
        self.assertEqual(response.status_code, 200)

    def test_get_product_and_check_content(self):
        """Тест: страница деталей содержит имя продукта"""
        response = self.client.get(
            reverse("shopapp:product_details", kwargs={"pk": self.product.pk})
        )
        self.assertContains(response, self.product.name)

    def test_get_product_404(self):
        """Тест: если продукт не найден → 404"""
        # Берём несуществующий pk
        invalid_pk = 9999
        response = self.client.get(
            reverse("shopapp:product_details", kwargs={"pk": invalid_pk})
        )
        self.assertEqual(response.status_code, 404)

class ProductsListViewTestCase(TestCase):
    fixtures = ['products-fixture.json']  # Загружаем фикстуры

    def test_products(self):
        """Тест: страница списка продуктов открывается и содержит продукты из фикстуры"""
        response = self.client.get(reverse("shopapp:products_list"))
        self.assertQuerySetEqual(
          qs=Product.objects.filter(archived=False).all(),
          values=(p.pk for p in response.context['products']),  
          transform=lambda p: p.pk,  
        )
        self.assertTemplateUsed(response, 'shopapp/products-list.html')

class OrdersListViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_user(username="Bob_test", password="qwerty")

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self) -> None:
        self.client.force_login(self.user)

    

    def test_orders_view(self):
        url = reverse("shopapp:order_list")

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Orders")

    # def test_orders_view_not_authenticated(self):
    #     self.client.logout()
    #     response = self.client.get(reverse("shopapp:order_list"))
    #     self.assertIn(str(settings.LOGIN_URL), response.url)
    #     self.assertEqual(response.status_code,302)

    def test_orders_view_not_authenticated(self):
        self.client.logout()
        response = self.client.get(reverse("shopapp:order_list"))
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)  # Проверяем, что в URL есть login
        self.assertIn(reverse('shopapp:order_list'), response.url)  # Проверяем next

class ProductsExportViewTestCase(TestCase):
    fixtures = ["products-fixture.json",

                ]
    def test_get_products_view(self):
        response = self.client.get(
            reverse("shopapp:products-export"),

        )
        self.assertEqual(response.status_code, 200)
        products = Product.objects.order_by("pk").all()
        expected_data = [
            {"pk":product.pk, "name":product.name, "price":str(product.price), "archived":product.archived,}
            for product in products
        ]

        products_data = response.json()
        self.assertEqual(
                products_data["products"],
                expected_data
            
        )


class OrderDetailViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            is_staff=True  # или дать права через permission
        )
        # Даём право view_order
        content_type = ContentType.objects.get_for_model(Order)
        permission = Permission.objects.get(
            codename='view_order',
            content_type=content_type
        )
        cls.user.user_permissions.add(permission)

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()
        super().tearDownClass()

    def setUp(self):
        self.client.force_login(self.user)
        # Создаём заказ
        self.order = Order.objects.create(
            user=self.user,
            delivery_address='Test Address 123',
            promocode='TEST123'
        )

    def tearDown(self):
        self.order.delete()

    def test_order_details(self):
        response = self.client.get(
            reverse('shopapp:order_details', kwargs={'pk': self.order.pk})
        )
        self.assertEqual(response.status_code, 200)
        # Проверяем, что в теле есть адрес и промокод
        self.assertContains(response, 'Test Address 123')
        self.assertContains(response, 'TEST123')
        # Проверяем контекст
        self.assertEqual(response.context['order'].pk, self.order.pk)