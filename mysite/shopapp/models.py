from django.db import models
from django.contrib.auth.models import User


# ============================================================
# ФУНКЦИЯ ДЛЯ СОХРАНЕНИЯ PREVIEW ТОВАРА
# ============================================================
#
# Эта функция определяет, куда Django будет сохранять
# главное изображение (preview) товара.
#
# ВАЖНО:
# При создании нового Product у него ещё может не быть pk.
# Поэтому здесь НЕ используем instance.pk.
#
# Иначе получаем:
# products/product.None/previews/Porsche911.jpg
#
# Вместо этого сохраняем preview в общую папку:
# products/previews/
#
def product_preview_directory_path(
    instance: "Product",
    filename: str,
) -> str:
    return f"products/previews/{filename}"


# ============================================================
# ТОВАР
# ============================================================

class Product(models.Model):

    class Meta:
        # Сортировка товаров:
        # сначала по названию,
        # затем по цене.
        ordering = ["name", "price"]

        # Старые настройки оставлены как комментарий.
        # db_table = "tech_products"
        # verbose_name_plural = "products"

    # --------------------------------------------------------
    # ОСНОВНЫЕ ДАННЫЕ ТОВАРА
    # --------------------------------------------------------

    # Название товара
    name = models.CharField(
        max_length=100
    )

    # Описание товара
    #
    # null=False означает, что в БД значение NULL
    # не используется.
    #
    # blank=True означает, что поле можно оставить
    # пустым в форме.
    description = models.TextField(
        null=False,
        blank=True
    )

    # Цена товара
    #
    # max_digits=12:
    # всего максимум 12 цифр.
    #
    # decimal_places=2:
    # две цифры после запятой.
    #
    # Например:
    # 1999.99
    price = models.DecimalField(
        default=0,
        max_digits=12,
        decimal_places=2
    )

    # Размер скидки
    discount = models.SmallIntegerField(
        default=0
    )

    # Дата и время создания товара
    #
    # auto_now_add=True означает:
    # Django автоматически записывает дату
    # при создании объекта.
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    # Архивный товар
    #
    # False = товар активен
    # True = товар отправлен в архив
    #
    # Мы используем это вместо физического удаления товара.
    archived = models.BooleanField(
        default=False
    )

    # --------------------------------------------------------
    # ПРОДАВЕЦ / СОЗДАТЕЛЬ ТОВАРА
    # --------------------------------------------------------

    # Связываем товар с пользователем.
    #
    # Один пользователь может создать много товаров.
    #
    # ForeignKey:
    # User 1 -------- N Product
    #
    # PROTECT означает:
    # нельзя удалить пользователя,
    # если у него остались товары.
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="Created by"
    )

    # --------------------------------------------------------
    # ГЛАВНОЕ ИЗОБРАЖЕНИЕ ТОВАРА
    # --------------------------------------------------------

    # Preview — основная фотография товара.
    #
    # null=True:
    # в БД может отсутствовать значение.
    #
    # blank=True:
    # поле можно оставить пустым в форме.
    #
    # upload_to:
    # Django использует нашу функцию,
    # чтобы определить путь сохранения файла.
    preview = models.ImageField(
        null=True,
        blank=True,
        upload_to=product_preview_directory_path
    )

    # --------------------------------------------------------
    # СТАРЫЙ МЕТОД КОРОТКОГО ОПИСАНИЯ
    # --------------------------------------------------------
    #
    # Оставляем закомментированным,
    # потому что сейчас он проекту не нужен.
    #
    # @property
    # def description_short(self) -> str:
    #     if len(self.description) < 48:
    #         return self.description
    #     return self.description[:48] + "..."

    # --------------------------------------------------------
    # СТРОКОВОЕ ПРЕДСТАВЛЕНИЕ
    # --------------------------------------------------------

    def __str__(self):
        # Когда Django показывает Product,
        # будет отображаться название товара.
        return self.name


# ============================================================
# ФУНКЦИЯ ДЛЯ СОХРАНЕНИЯ ДОПОЛНИТЕЛЬНЫХ ФОТО
# ============================================================

def product_images_directory_path(
    instance: "ProductImage",
    filename: str,
) -> str:
    """
    Определяет путь для дополнительных изображений товара.

    Здесь мы уже можем использовать:

        instance.product.pk

    потому что ProductImage создаётся для уже существующего
    Product.

    Например:

        products/product_6/images/photo.jpg
    """

    return (
        f"products/product_{instance.product.pk}"
        f"/images/{filename}"
    )


# ============================================================
# ДОПОЛНИТЕЛЬНОЕ ИЗОБРАЖЕНИЕ ТОВАРА
# ============================================================

class ProductImage(models.Model):

    # Какому товару принадлежит фотография.
    #
    # Один Product может иметь много ProductImage.
    #
    # related_name="images" позволяет писать:
    #
    # product.images.all()
    #
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images"
    )

    # Сам файл изображения.
    #
    # Путь определяется функцией
    # product_images_directory_path.
    image = models.ImageField(
        upload_to=product_images_directory_path
    )

    # Дополнительное описание изображения.
    description = models.CharField(
        max_length=200,
        null=False,
        blank=True
    )


# ============================================================
# ЗАКАЗ
# ============================================================

class Order(models.Model):

    # Адрес доставки.
    #
    # Может быть пустым.
    delivery_address = models.TextField(
        null=True,
        blank=True
    )

    # Промокод.
    #
    # Максимум 20 символов.
    promocode = models.CharField(
        max_length=20,
        null=False,
        blank=True
    )

    # Дата и время создания заказа.
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    # Пользователь, который оформил заказ.
    #
    # Один пользователь может иметь много заказов.
    #
    # PROTECT:
    # нельзя удалить пользователя,
    # если существуют его заказы.
    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT
    )

    # Товары в заказе.
    #
    # ManyToMany означает:
    #
    # один заказ → много товаров
    # один товар → может находиться во многих заказах
    #
    # Например:
    #
    # Order №1
    #   ├── Laptop
    #   ├── Mouse
    #   └── Keyboard
    #
    products = models.ManyToManyField(
        Product,
        related_name="orders"
    )

    # Файл чека.
    #
    # Чеки сохраняются в:
    #
    # uploads/orders/receipts/
    receipt = models.FileField(
        null=True,
        upload_to="orders/receipts/"
    )