from django.core.management import BaseCommand
from shopapp.models import Product

class Command(BaseCommand):
    '''
    Creates product
    '''

    def handle(self, *args, **options):
        self.stdout.write("Create Products")

        products_name = [
            "Laptop",
            "Desktop",
            "Smartpone"
        ]
        for product_name in products_name:

            product, created = Product.objects.get_or_create(name=product_name)
            self.stdout.write(f'Create product {product.name}')
        

        self.stderr.write(self.style.SUCCESS("product created"))

