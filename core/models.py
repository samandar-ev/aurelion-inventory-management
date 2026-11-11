from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

# Role hierarchy: Owner > Cashier > Sales Associate (each role inherits the ones below it).
class User(AbstractUser):
    class Role(models.TextChoices):
        OWNER = 'OWNER', _('Owner')
        CASHIER = 'CASHIER', _('Cashier')
        SALES_ASSOCIATE = 'SALES_ASSOCIATE', _('Sales Associate')

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.SALES_ASSOCIATE)
    
    def is_owner(self):
        return self.role == self.Role.OWNER

    def is_cashier(self):
        return self.role == self.Role.CASHIER or self.is_owner()

    def is_sales_associate(self):
        return self.role == self.Role.SALES_ASSOCIATE or self.is_cashier()

class Location(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    address = models.TextField()
    is_store = models.BooleanField(default=True)
    is_warehouse = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class ProductImage(models.Model):
    """Additional product images"""
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='additional_images')
    image = models.ImageField(upload_to='products/gallery/')
    is_primary = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order', 'id']
    
    def __str__(self):
        return f"{self.product.name} - Image {self.order}"

class Product(models.Model):
    BRAND_CHOICES = [
        ('Gucci', 'Gucci'), ('Prada', 'Prada'), ('Louis Vuitton', 'Louis Vuitton'), 
        ('Hermès', 'Hermès'), ('Chanel', 'Chanel'), ('Dior', 'Dior'), 
        ('Balenciaga', 'Balenciaga'), ('Saint Laurent', 'Saint Laurent'), 
        ('Burberry', 'Burberry'), ('Fendi', 'Fendi'), ('Versace', 'Versace'),
        ('Valentino', 'Valentino'), ('Givenchy', 'Givenchy'), ('Bottega Veneta', 'Bottega Veneta'),
        ('Loewe', 'Loewe'), ('Celine', 'Celine'), ('Alexander McQueen', 'Alexander McQueen'),
        ('Dolce & Gabbana', 'Dolce & Gabbana'), ('Tom Ford', 'Tom Ford'), ('The Row', 'The Row'),
        ('Brunello Cucinelli', 'Brunello Cucinelli'), ('Loro Piana', 'Loro Piana'),
        ('Other', 'Other')
    ]

    MATERIAL_CHOICES = [
        ('Cotton', 'Cotton'), ('Silk', 'Silk'), ('Wool', 'Wool'), ('Cashmere', 'Cashmere'),
        ('Linen', 'Linen'), ('Leather', 'Leather'), ('Denim', 'Denim'), ('Velvet', 'Velvet'),
        ('Satin', 'Satin'), ('Chiffon', 'Chiffon'), ('Tweed', 'Tweed'), ('Polyester', 'Polyester'),
        ('Viscose', 'Viscose'), ('Nylon', 'Nylon'), ('Elastane', 'Elastane'),
        ('Other', 'Other'), ('Blend', 'Blend')
    ]
    
    CATEGORY_CHOICES = [
        ('Bags', 'Bags'),
        ('Shoes', 'Shoes'),
        ('Accessories', 'Accessories'),
        ('Clothing', 'Clothing'),
        ('Jewelry', 'Jewelry'),
        ('Watches', 'Watches'),
        ('Eyewear', 'Eyewear'),
        ('Fragrance', 'Fragrance'),
    ]
    
    CONDITION_CHOICES = [
        ('New', 'New'),
        ('Display', 'Display'),
        ('Vintage', 'Vintage'),
        ('Like New', 'Like New'),
    ]
    
    PACKAGING_CONDITION_CHOICES = [
        ('Pristine', 'Pristine / Like New'),
        ('Complete', 'Complete - Minor Wear'),
        ('Partial', 'Partial - Missing Components'),
        ('Worn', 'Worn / Damaged'),
    ]

    brand = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Accessories')
    collection = models.CharField(max_length=100, blank=True)
    season = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)
    
    base_sku = models.CharField(max_length=50, unique=True)
    supplier_product_code = models.CharField(max_length=100, blank=True)
    
    material = models.CharField(max_length=100, blank=True)
    material_composition = models.TextField(blank=True, help_text="Specific blend details or other material name")
    
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='New')
    release_year = models.IntegerField(null=True, blank=True)
    is_limited_edition = models.BooleanField(default=False)
    
    has_box = models.BooleanField(default=False)
    has_dust_bag = models.BooleanField(default=False)
    has_warranty_card = models.BooleanField(default=False)
    has_care_card = models.BooleanField(default=False)
    has_extras = models.BooleanField(default=False)
    packaging_notes = models.TextField(blank=True)
    packaging_condition = models.CharField(max_length=50, blank=True, choices=PACKAGING_CONDITION_CHOICES)
    provenance_notes = models.TextField(blank=True)
    
    country_of_origin = models.CharField(max_length=100, blank=True)
    
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    
    internal_tags = models.TextField(blank=True, help_text="Comma-separated tags")
    keywords = models.TextField(blank=True)
    display_notes = models.TextField(blank=True)
    is_luxury_product = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.brand} {self.name}"
    
    @property
    def total_quantity(self):
        return sum(v.initial_quantity for v in self.variants.all())

class ProductVariant(models.Model):
    HARDWARE_CHOICES = [
        ('Gold', 'Gold'),
        ('Silver', 'Silver'),
        ('Palladium', 'Palladium'),
        ('Rose Gold', 'Rose Gold'),
        ('Ruthenium', 'Ruthenium'),
        ('Brass', 'Brass'),
        ('None', 'None'),
    ]
    
    CURRENCY_CHOICES = [
        ('USD', 'USD'),
        ('EUR', 'EUR'),
        ('GBP', 'GBP'),
        ('UZS', 'UZS'),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    sku = models.CharField(max_length=50, unique=True)
    
    color = models.CharField(max_length=50)
    size = models.CharField(max_length=20)
    hardware_type = models.CharField(max_length=50, choices=HARDWARE_CHOICES, blank=True)
    variant_material = models.CharField(max_length=100, blank=True)
    
    cost_price = models.DecimalField(max_digits=10, decimal_places=2)
    retail_price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='USD')
    
    serial_number = models.CharField(max_length=100, blank=True, unique=True, null=True)
    authentication_code = models.CharField(max_length=100, blank=True)
    edition_number = models.CharField(max_length=50, blank=True)
    
    initial_quantity = models.PositiveIntegerField(default=1)
    storage_location = models.ForeignKey(Location, on_delete=models.PROTECT, null=True, blank=True)
    minimum_stock_level = models.PositiveIntegerField(default=1)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('product', 'color', 'size')

    def __str__(self):
        return f"{self.product.name} - {self.color} / {self.size}"
    
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.retail_price and self.cost_price and self.retail_price < self.cost_price:
            raise ValidationError('Retail price cannot be lower than cost price.')

class Barcode(models.Model):
    class Type(models.TextChoices):
        EAN13 = 'EAN13', _('EAN-13')
        UPC = 'UPC', _('UPC')
        CODE128 = 'CODE128', _('Code 128')
        INTERNAL = 'INTERNAL', _('Internal')

    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name='barcodes')
    code = models.CharField(max_length=100, unique=True)
    barcode_type = models.CharField(max_length=20, choices=Type.choices, default=Type.INTERNAL)

    def __str__(self):
        return self.code

class StockLevel(models.Model):
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name='stock_levels')
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='stock_levels')
    quantity_on_hand = models.IntegerField(default=0)
    quantity_reserved = models.IntegerField(default=0)
    quantity_sold = models.IntegerField(default=0)

    class Meta:
        unique_together = ('variant', 'location')

    def __str__(self):
        return f"{self.variant} @ {self.location}: {self.quantity_on_hand}"

class StockMovement(models.Model):
    class Type(models.TextChoices):
        IN = 'IN', _('In')
        OUT = 'OUT', _('Out')
        ADJUST = 'ADJUST', _('Adjustment')
        TRANSFER = 'TRANSFER', _('Transfer')

    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    from_location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True, related_name='movements_from')
    to_location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True, related_name='movements_to')
    quantity = models.PositiveIntegerField()
    movement_type = models.CharField(max_length=20, choices=Type.choices)
    reason = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

class Client(models.Model):
    class LoyaltyTier(models.TextChoices):
        REGULAR = 'REGULAR', _('Regular')
        SILVER = 'SILVER', _('Silver')
        GOLD = 'GOLD', _('Gold')
        PLATINUM = 'PLATINUM', _('Platinum')

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    birthday = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    prefers_communication = models.BooleanField(default=True)
    loyalty_tier = models.CharField(max_length=20, choices=LoyaltyTier.choices, default=LoyaltyTier.REGULAR, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_tier(self):
        """Returns manual tier if set, otherwise calculates dynamically."""
        if self.loyalty_tier and self.loyalty_tier != self.LoyaltyTier.REGULAR:
            return self.loyalty_tier
        return self.dynamic_tier()

    def dynamic_tier(self):
        from django.db.models import Sum
        orders = self.order_set.filter(status=Order.Status.COMPLETED)
        visits = orders.count()
        total = orders.aggregate(total=Sum('total_amount'))['total'] or 0
        if visits >= 12 and total >= 5000:
            return self.LoyaltyTier.PLATINUM
        if visits >= 6 and total >= 1000:
            return self.LoyaltyTier.GOLD
        if visits >= 1:
            return self.LoyaltyTier.SILVER
        return self.LoyaltyTier.REGULAR

    def dynamic_tier_label(self):
        return self.LoyaltyTier(self.get_tier()).label

    def __str__(self):
        return f"{self.first_name} {self.last_name}".strip()

class LoyaltyAccount(models.Model):
    class Tier(models.TextChoices):
        REGULAR = 'REGULAR', _('Regular')
        VIP = 'VIP', _('VIP')
        VVIP = 'VVIP', _('VVIP')
        STAFF = 'STAFF', _('Staff')

    client = models.OneToOneField(Client, on_delete=models.CASCADE, related_name='loyalty_account')
    points_balance = models.IntegerField(default=0)
    tier = models.CharField(max_length=20, choices=Tier.choices, default=Tier.REGULAR)

    def __str__(self):
        return f"{self.client} - {self.tier}"

class DiscountRule(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    is_active = models.BooleanField(default=True)
    requires_manager_approval = models.BooleanField(default=False)
    min_points_required = models.IntegerField(default=0)
    applicable_to_tier = models.CharField(max_length=20, choices=LoyaltyAccount.Tier.choices, null=True, blank=True)

    def __str__(self):
        return self.name

class Order(models.Model):
    class Type(models.TextChoices):
        SALE = 'SALE', _('Sale')
        RETURN = 'RETURN', _('Return')
        EXCHANGE = 'EXCHANGE', _('Exchange')
    
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', _('Draft')
        CANCELLED = 'CANCELLED', _('Cancelled')
        
        COMPLETED = 'COMPLETED', _('Completed')
        PARTIALLY_RETURNED = 'PARTIALLY_RETURNED', _('Partially Returned')
        FULLY_RETURNED = 'FULLY_RETURNED', _('Fully Returned')
        
        REFUNDED = 'REFUNDED', _('Refunded')
        REFUND_PENDING = 'REFUND_PENDING', _('Refund Pending')

    type = models.CharField(
        max_length=20,
        choices=Type.choices,
        default=Type.SALE,
        db_index=True
    )
    parent_order = models.ForeignKey(
        'self',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='child_orders',
        help_text='For RETURN/EXCHANGE orders, this points to the original SALE order'
    )
    order_code = models.CharField(max_length=12, unique=True, blank=True, null=True, default=None)
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True)
    location = models.ForeignKey(Location, on_delete=models.PROTECT)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=25, choices=Status.choices, default=Status.DRAFT)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    loyalty_points_earned = models.IntegerField(default=0)
    loyalty_points_redeemed = models.IntegerField(default=0)

    def __str__(self):
        return f"Order #{self.order_code or self.id}"

    @classmethod
    def generate_code(cls):
        import random
        import string
        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            if not cls.objects.filter(order_code=code).exists():
                return code

    def save(self, *args, **kwargs):
        # Every order carries a short code staff can read off a receipt
        if not self.order_code:
            self.order_code = self.generate_code()
        super().save(*args, **kwargs)

    @property
    def ui_status(self):
        """Returns display-friendly status"""
        if self.type == self.Type.EXCHANGE:
            return 'EXCHANGE'
        elif self.type == self.Type.RETURN:
            return 'RETURN'
        return self.status

class AppliedDiscount(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='discounts')
    rule = models.ForeignKey(DiscountRule, on_delete=models.PROTECT)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    variant = models.ForeignKey(ProductVariant, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    line_discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    qty_returned = models.PositiveIntegerField(
        default=0,
        help_text='Total quantity returned or exchanged from this line item'
    )

    @property
    def line_total(self):
        return (self.unit_price * self.quantity) - self.line_discount
    
    @property
    def qty_remaining(self):
        """Quantity still available for return/exchange"""
        return max(0, self.quantity - self.qty_returned)
    
    @property
    def is_fully_returned(self):
        """Check if all items from this line have been returned"""
        return self.qty_returned >= self.quantity
    
    def clean(self):
        """Validate that qty_returned doesn't exceed quantity"""
        super().clean()
        if self.qty_returned > self.quantity:
            from django.core.exceptions import ValidationError
            raise ValidationError({
                'qty_returned': f'Cannot return more than purchased quantity ({self.quantity})'
            })
    
    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(qty_returned__lte=models.F('quantity')),
                name='qty_returned_lte_quantity'
            )
        ]

class Return(models.Model):
    class Reason(models.TextChoices):
        CHANGED_MIND = 'CHANGED_MIND', _('Changed my mind')
        DEFECTIVE = 'DEFECTIVE', _('Defective / Damaged')
        WRONG_SIZE = 'WRONG_SIZE', _('Wrong size')
        WRONG_ITEM = 'WRONG_ITEM', _('Wrong item delivered')
        OTHER = 'OTHER', _('Other')

    class Action(models.TextChoices):
        REFUND = 'REFUND', _('Refund')
        EXCHANGE = 'EXCHANGE', _('Exchange')

    original_order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name='returns')
    refund_order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True, related_name='refund_source')
    replacement_order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True, related_name='replacement_source')
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    reason = models.CharField(max_length=50, choices=Reason.choices, default=Reason.OTHER)
    action = models.CharField(max_length=20, choices=Action.choices, default=Action.REFUND)

    def __str__(self):
        return f"Return for {self.original_order} ({self.get_action_display()})"

class ReturnItem(models.Model):
    return_process = models.ForeignKey(Return, on_delete=models.CASCADE, related_name='items')
    order_item = models.ForeignKey(OrderItem, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    reason = models.CharField(max_length=50, choices=Return.Reason.choices, blank=True, null=True)

    def __str__(self):
        return f"{self.quantity} x {self.order_item.variant} (Return)"


class Promotion(models.Model):
    """
    Comprehensive promotion system supporting:
    - Percentage off
    - Fixed amount off
    - BOGO (Buy X Get Y Free)
    - Tiered discounts based on customer loyalty
    - Bundle discounts
    """
    class Type(models.TextChoices):
        PERCENTAGE = 'PERCENTAGE', _('Percentage Off')
        FIXED = 'FIXED', _('Fixed Amount Off')
        BOGO = 'BOGO', _('Buy X Get Y Free')
        TIERED = 'TIERED', _('Tier-Based Discount')
        BUNDLE = 'BUNDLE', _('Bundle Discount')

    class AppliesTo(models.TextChoices):
        ALL = 'ALL', _('All Products')
        CATEGORY = 'CATEGORY', _('Specific Category')
        BRAND = 'BRAND', _('Specific Brand')
        PRODUCTS = 'PRODUCTS', _('Selected Products')

    class CustomerTierRestriction(models.TextChoices):
        ALL = 'ALL', _('All Customers')
        SILVER = 'SILVER', _('Silver & Above')
        GOLD = 'GOLD', _('Gold & Above')
        PLATINUM = 'PLATINUM', _('Platinum Only')

    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True, blank=True, null=True, help_text="Optional promo code")
    description = models.TextField(blank=True)
    
    promo_type = models.CharField(max_length=20, choices=Type.choices, default=Type.PERCENTAGE)
    
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, default=0, 
                                          help_text="Percentage (0-100) or fixed amount")
    
    buy_quantity = models.PositiveIntegerField(default=2, help_text="Buy X items...")
    get_quantity = models.PositiveIntegerField(default=1, help_text="...get Y free (cheapest item)")
    
    silver_discount = models.DecimalField(max_digits=5, decimal_places=2, default=5)
    gold_discount = models.DecimalField(max_digits=5, decimal_places=2, default=10)
    platinum_discount = models.DecimalField(max_digits=5, decimal_places=2, default=15)
    
    applies_to = models.CharField(max_length=20, choices=AppliesTo.choices, default=AppliesTo.ALL)
    category = models.CharField(max_length=50, blank=True, choices=Product.CATEGORY_CHOICES)
    brand = models.CharField(max_length=100, blank=True)
    
    customer_tier = models.CharField(max_length=20, choices=CustomerTierRestriction.choices, default=CustomerTierRestriction.ALL)
    
    min_purchase = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                        help_text="Minimum cart value to apply")
    min_items = models.PositiveIntegerField(default=0, help_text="Minimum items in cart")
    
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    
    max_uses = models.PositiveIntegerField(default=0, help_text="0 = unlimited")
    used_count = models.PositiveIntegerField(default=0)
    max_uses_per_customer = models.PositiveIntegerField(default=0, help_text="0 = unlimited")
    
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def is_valid(self):
        """Check if promotion is currently valid."""
        now = timezone.now()
        if not self.is_active:
            return False
        if now < self.start_date or now > self.end_date:
            return False
        if self.max_uses > 0 and self.used_count >= self.max_uses:
            return False
        return True

    def get_status(self):
        now = timezone.now()
        if not self.is_active:
            return 'Disabled'
        if now < self.start_date:
            return 'Scheduled'
        if now > self.end_date:
            return 'Expired'
        if self.max_uses > 0 and self.used_count >= self.max_uses:
            return 'Exhausted'
        return 'Active'

    def can_apply_to_customer(self, client):
        """Check if promotion applies to customer tier."""
        if self.customer_tier == self.CustomerTierRestriction.ALL:
            return True
        if not client:
            return False
        
        tier = client.get_tier()
        tier_hierarchy = [Client.LoyaltyTier.REGULAR, Client.LoyaltyTier.SILVER, 
                          Client.LoyaltyTier.GOLD, Client.LoyaltyTier.PLATINUM]
        
        customer_rank = tier_hierarchy.index(tier) if tier in tier_hierarchy else 0
        
        if self.customer_tier == self.CustomerTierRestriction.SILVER:
            return customer_rank >= 1
        if self.customer_tier == self.CustomerTierRestriction.GOLD:
            return customer_rank >= 2
        if self.customer_tier == self.CustomerTierRestriction.PLATINUM:
            return customer_rank >= 3
        return False

    def applies_to_product(self, product):
        """Check if promotion applies to a specific product."""
        if self.applies_to == self.AppliesTo.ALL:
            return True
        if self.applies_to == self.AppliesTo.CATEGORY:
            return product.category == self.category
        if self.applies_to == self.AppliesTo.BRAND:
            return product.brand == self.brand
        if self.applies_to == self.AppliesTo.PRODUCTS:
            return self.products.filter(id=product.id).exists()
        return False

    def calculate_discount(self, cart_items, client=None):
        """
        Calculate the discount for given cart items.
        Returns (discount_amount, discount_description)
        """
        from decimal import Decimal
        
        if not self.is_valid():
            return Decimal('0'), ''
        
        if not self.can_apply_to_customer(client):
            return Decimal('0'), ''

        applicable_items = []
        for item in cart_items:
            product = item.get('product') or item.get('variant').product
            if self.applies_to_product(product):
                applicable_items.append(item)

        if not applicable_items:
            return Decimal('0'), ''

        applicable_total = sum(
            Decimal(str(item.get('price', 0))) * item.get('qty', 1) 
            for item in applicable_items
        )
        total_items = sum(item.get('qty', 1) for item in applicable_items)

        if applicable_total < self.min_purchase:
            return Decimal('0'), ''
        if total_items < self.min_items:
            return Decimal('0'), ''

        discount = Decimal('0')
        description = ''

        if self.promo_type == self.Type.PERCENTAGE:
            discount = applicable_total * (Decimal(str(self.discount_value)) / 100)
            description = f'{self.discount_value}% off'

        elif self.promo_type == self.Type.FIXED:
            discount = min(Decimal(str(self.discount_value)), applicable_total)
            description = f'${self.discount_value} off'

        elif self.promo_type == self.Type.BOGO:
            all_prices = []
            for item in applicable_items:
                price = Decimal(str(item.get('price', 0)))
                for _ in range(item.get('qty', 1)):
                    all_prices.append(price)
            
            all_prices.sort()
            
            total_qty = len(all_prices)
            sets = total_qty // (self.buy_quantity + self.get_quantity)
            free_items = sets * self.get_quantity
            
            if free_items > 0:
                discount = sum(all_prices[:free_items])
                description = f'Buy {self.buy_quantity} Get {self.get_quantity} Free'

        elif self.promo_type == self.Type.TIERED:
            if client:
                tier = client.get_tier()
                if tier == Client.LoyaltyTier.PLATINUM:
                    rate = self.platinum_discount
                elif tier == Client.LoyaltyTier.GOLD:
                    rate = self.gold_discount
                elif tier == Client.LoyaltyTier.SILVER:
                    rate = self.silver_discount
                else:
                    rate = Decimal('0')
                
                if rate > 0:
                    discount = applicable_total * (rate / 100)
                    description = f'{rate}% VIP discount'

        return discount.quantize(Decimal('0.01')), description


class PromotionProduct(models.Model):
    """Links specific products to a promotion."""
    promotion = models.ForeignKey(Promotion, on_delete=models.CASCADE, related_name='product_links')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='promotions')

    class Meta:
        unique_together = ('promotion', 'product')

    def __str__(self):
        return f"{self.promotion.name} - {self.product.name}"


class PromotionUsage(models.Model):
    """Track promotion usage per customer."""
    promotion = models.ForeignKey(Promotion, on_delete=models.CASCADE, related_name='usages')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, null=True, blank=True)
    order = models.ForeignKey('Order', on_delete=models.CASCADE)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    used_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.promotion.name} used on Order #{self.order.id}"
