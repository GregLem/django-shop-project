from django.core.management import BaseCommand
from django.contrib.auth.models import User
from shopapp.models import Order, Product


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write('Create order')
        user = User.objects.get(username='Grisha')
        order, created = Order.objects.get_or_create(
            delivery_address = 'ul Vishnevay, d 8',
            promocode = "SALE123",
            user = user,    
        )
        self.stdout.write(f"Created order {order.id}")

        products = Product.objects.all()

        order.products.set(products)

        self.stdout.write(
            self.style.SUCCESS(
                f"Order #{order.id} created and linked with {products.count()} products"
            )
        )