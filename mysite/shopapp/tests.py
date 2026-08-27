# shopapp/tests.py

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from .models import Product

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
        self.assertEqual(product.price, 9.99)
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