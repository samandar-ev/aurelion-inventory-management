"""Fill a local database with a believable boutique: staff, a photographed
catalogue, clients, promotions, seven weeks of sales and a couple of returns.

    python manage.py migrate
    python manage.py seed_demo --reset

Local demos only. Every account gets the same password (default: aurelion-demo).
"""
import random
from datetime import datetime, time, timedelta
from decimal import Decimal
from pathlib import Path

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from core.models import (
    Barcode, Client, Location, Order, OrderItem, Product, ProductImage, ProductVariant,
    Promotion, PromotionUsage, Return, ReturnItem, StockLevel, User,
)

PHOTOS = Path(__file__).resolve().parents[2] / 'demo' / 'products'

STAFF = [
    # username, first, last, role
    ('owner', 'Isabelle', 'Laurent', User.Role.OWNER),
    ('cashier', 'Marco', 'Bellini', User.Role.CASHIER),
    ('sofia', 'Sofia', 'Reyes', User.Role.CASHIER),
    ('associate', 'Amara', 'Okafor', User.Role.SALES_ASSOCIATE),
    ('theo', 'Theo', 'Lindqvist', User.Role.SALES_ASSOCIATE),
]

# photo, brand, name, category, material, season, collection, variants [(color, size, retail, qty)]
CATALOGUE = [
    ('chanel-classic-flap', 'Chanel', 'Classic Flap Bag Medium', 'Bags', 'Leather', 'Permanent', 'Classic',
     [('Black lambskin', 'Medium', '10200', 2), ('Beige caviar', 'Medium', '10200', 1)]),
    ('dior-lady-dior-rose', 'Dior', 'Lady Dior Medium', 'Bags', 'Leather', 'SS26', 'Lady Dior',
     [('Rose des Vents', 'Medium', '6500', 2)]),
    ('saint-laurent-le-5-a-7', 'Saint Laurent', 'Le 5 à 7 Hobo Bag', 'Bags', 'Leather', 'FW25', '',
     [('Black', 'One size', '2950', 3)]),
    ('bottega-veneta-mini-jodie', 'Bottega Veneta', 'Mini Jodie Intrecciato', 'Bags', 'Leather', 'SS26', 'Jodie',
     [('Emerald', 'Mini', '3100', 1), ('Fondant', 'Mini', '3100', 4)]),
    ('celine-triomphe-small', 'Celine', 'Triomphe Small Bag', 'Bags', 'Leather', 'SS26', 'Triomphe',
     [('Chalk', 'Small', '3650', 3)]),
    ('rolex-submariner-date', 'Rolex', 'Submariner Date 126619LB', 'Watches', 'Other', '', 'Professional',
     [('Blue dial, white gold', '41 mm', '44500', 0)]),
    ('omega-aqua-terra', 'Omega', 'Seamaster Aqua Terra 41', 'Watches', 'Other', '', 'Seamaster',
     [('Blue dial, steel and Sedna gold', '41 mm', '9800', 2)]),
    ('iwc-portugieser', 'IWC', 'Portugieser Chronograph', 'Watches', 'Leather', '', 'Portugieser',
     [('Silver dial, black strap', '41 mm', '8900', 3)]),
    ('rolex-day-date', 'Rolex', 'Day-Date 40', 'Watches', 'Other', '', 'Day-Date',
     [('Silver Roman dial', '40 mm', '39650', 1)]),
    ('tiffany-chain-bracelet', 'Tiffany & Co.', 'HardWear Link Bracelet', 'Jewelry', 'Other', '', 'HardWear',
     [('18K yellow gold', 'Medium', '7400', 2)]),
    ('cartier-love-bracelet', 'Cartier', 'Love Bracelet', 'Jewelry', 'Other', '', 'Love',
     [('18K yellow gold', '16', '7350', 1), ('18K yellow gold', '17', '7350', 2), ('18K rose gold', '17', '7350', 0)]),
    ('tiffany-diamond-line-bracelet', 'Tiffany & Co.', 'Victoria Line Bracelet', 'Jewelry', 'Other', '', 'Victoria',
     [('Platinum, diamonds', 'Medium', '21500', 1)]),
    ('louboutin-so-kate', 'Christian Louboutin', 'So Kate 120 Pump', 'Shoes', 'Leather', 'Permanent', '',
     [('Black patent', '37', '795', 2), ('Black patent', '38', '795', 3), ('Black patent', '39', '795', 1)]),
    ('balenciaga-triple-s', 'Balenciaga', 'Triple S Sneaker', 'Shoes', 'Other', 'FW25', '',
     [('White', '42', '1150', 2), ('White', '43', '1150', 4)]),
    ('louis-vuitton-trainer', 'Louis Vuitton', 'LV Trainer Sneaker', 'Shoes', 'Leather', 'SS26', '',
     [('Black and white', '42', '1390', 3), ('Black and white', '44', '1390', 2)]),
    ('loro-piana-cashmere-crewneck', 'Loro Piana', 'Baby Cashmere Crewneck', 'Clothing', 'Cashmere', 'FW25', '',
     [('Grey melange', 'M', '1850', 5), ('Grey melange', 'L', '1850', 3), ('Navy', 'M', '1850', 2)]),
    ('brunello-cucinelli-cardigan', 'Brunello Cucinelli', 'Cashmere Rib Cardigan', 'Clothing', 'Cashmere', 'FW25', '',
     [('Oatmeal', 'S', '3450', 2), ('Oatmeal', 'M', '3450', 3)]),
    ('prada-symbole-sunglasses', 'Prada', 'Symbole Sunglasses', 'Eyewear', 'Other', 'SS26', 'Symbole',
     [('Black', 'One size', '480', 6)]),
    ('hermes-silk-twill-scarf', 'Hermès', 'Silk Twill Scarf 90', 'Accessories', 'Silk', 'FW25', 'Carré',
     [('Coral and blush', '90 cm', '565', 7)]),
]

CLIENTS = [
    ('Eleanor', 'Whitcombe', '+1 212 555 0148', 'eleanor.whitcombe@example.com', 'PLATINUM', 'Prefers private appointments. Collects Hermès scarves.'),
    ('Jonathan', 'Ashby', '+1 212 555 0172', 'j.ashby@example.com', 'GOLD', 'Watch collector, interested in Rolex allocations.'),
    ('Mei', 'Tanaka', '+1 646 555 0119', 'mei.tanaka@example.com', 'GOLD', 'Size 37 shoes. Likes quiet colours.'),
    ('Charlotte', 'Devereux', '+1 917 555 0133', 'charlotte.d@example.com', 'PLATINUM', 'Annual gift purchases in December.'),
    ('Rafael', 'Montoya', '+1 646 555 0187', 'rafael.montoya@example.com', 'SILVER', ''),
    ('Priya', 'Raman', '+1 212 555 0164', 'priya.raman@example.com', 'SILVER', 'Prefers text messages over calls.'),
    ('Henry', 'Calloway', '+1 917 555 0102', '', 'REGULAR', ''),
    ('Ines', 'Moreau', '+1 212 555 0191', 'ines.moreau@example.com', 'GOLD', 'Cashmere size M.'),
    ('Daniel', 'Okonkwo', '+1 646 555 0145', 'daniel.ok@example.com', 'REGULAR', ''),
    ('Sophie', 'Lindgren', '+1 917 555 0126', 'sophie.lindgren@example.com', 'SILVER', ''),
    ('Victoria', 'Hale', '+1 212 555 0157', 'victoria.hale@example.com', 'PLATINUM', 'Bridal party shopping in spring.'),
    ('Arjun', 'Mehta', '+1 646 555 0110', '', 'REGULAR', ''),
]


class Command(BaseCommand):
    help = 'Create demo staff, a photographed catalogue, clients, promotions, sales and returns (local only).'

    def add_arguments(self, parser):
        parser.add_argument('--reset', action='store_true', help='Delete existing catalogue, clients, orders and promotions first.')
        parser.add_argument('--password', default='aurelion-demo', help='Password for every demo account.')
        parser.add_argument('--seed', type=int, default=11, help='Random seed, so runs are repeatable.')

    @transaction.atomic
    def handle(self, *args, reset, password, seed, **options):
        rng = random.Random(seed)
        if reset:
            self._reset()

        location, _ = Location.objects.get_or_create(code='MAIN', defaults={'name': 'Flagship store', 'address': '725 Madison Avenue, New York'})
        staff = self._staff(password)
        variants = self._catalogue(location, rng)
        clients = self._clients(rng)
        promos = self._promotions(staff['owner'])
        orders = self._sales(location, staff, variants, clients, promos, rng)
        self._returns(orders, staff, rng)

        self.stdout.write(self.style.SUCCESS(
            f'Demo ready: {len(staff)} staff, {Product.objects.count()} products, {len(variants)} variants, '
            f'{len(clients)} clients, {Order.objects.count()} orders. Password for every account: {password}'
        ))

    def _reset(self):
        PromotionUsage.objects.all().delete()
        ReturnItem.objects.all().delete()
        Return.objects.all().delete()
        OrderItem.objects.all().delete()
        Order.objects.all().delete()
        Promotion.objects.all().delete()
        Client.objects.all().delete()
        Barcode.objects.all().delete()
        StockLevel.objects.all().delete()
        ProductImage.objects.all().delete()
        ProductVariant.objects.all().delete()
        for product in Product.objects.all():
            if product.image:
                product.image.delete(save=False)
        Product.objects.all().delete()

    def _staff(self, password):
        staff = {}
        for username, first, last, role in STAFF:
            user, _ = User.objects.get_or_create(username=username)
            user.first_name, user.last_name, user.role = first, last, role
            user.is_staff = user.is_superuser = role == User.Role.OWNER
            user.set_password(password)
            user.save()
            staff[username] = user
        return staff

    def _catalogue(self, location, rng):
        variants = []
        self.by_photo = {}
        for photo, brand, name, category, material, season, collection, rows in CATALOGUE:
            base = ''.join(w[0] for w in brand.replace('&', '').split())[:3].upper() + '-' + photo.split('-', 1)[1][:14].upper().replace('-', '')
            product = Product(
                brand=brand, name=name, category=category, material=material, season=season,
                collection=collection, base_sku=base, condition='New', is_luxury_product=True,
                country_of_origin='Switzerland' if category == 'Watches' else ('France' if brand in ('Chanel', 'Dior', 'Hermès', 'Saint Laurent', 'Celine', 'Louis Vuitton', 'Christian Louboutin', 'Cartier') else 'Italy'),
                has_box=True, has_dust_bag=category in ('Bags', 'Shoes'), has_warranty_card=category in ('Watches', 'Jewelry'),
                description=f'{brand} {name}. Stand-in photography for the demo catalogue.',
            )
            path = PHOTOS / f'{photo}.jpg'
            if path.exists():
                product.image.save(path.name, ContentFile(path.read_bytes()), save=False)
            product.save()
            for i, (color, size, retail, qty) in enumerate(rows, start=1):
                retail = Decimal(retail)
                variant = ProductVariant.objects.create(
                    product=product, sku=f'{base}-{i:02d}', color=color, size=size,
                    cost_price=(retail * Decimal(rng.choice(['0.52', '0.55', '0.58', '0.61']))).quantize(Decimal('1')),
                    retail_price=retail, currency='USD', initial_quantity=qty, minimum_stock_level=2 if retail < 2000 else 1,
                    serial_number=f'SN{rng.randint(10**7, 10**8 - 1)}' if category in ('Watches', 'Jewelry') else None,
                    storage_location=location,
                )
                Barcode.objects.create(variant=variant, code=f'AUR{variant.pk:09d}', barcode_type=Barcode.Type.CODE128)
                self.by_photo.setdefault(photo, []).append(variant)
                StockLevel.objects.get_or_create(variant=variant, location=location, defaults={'quantity_on_hand': qty})
                variants.append(variant)
        return variants

    def _clients(self, rng):
        clients = []
        for first, last, phone, email, tier, notes in CLIENTS:
            client, _ = Client.objects.update_or_create(phone=phone, defaults=dict(
                first_name=first, last_name=last, email=email or None, loyalty_tier=tier, notes=notes,
                birthday=datetime(rng.randint(1958, 1996), rng.randint(1, 12), rng.randint(1, 28)).date(),
            ))
            clients.append(client)
        return clients

    def _promotions(self, owner):
        now = timezone.now()
        make = lambda **kw: Promotion.objects.create(created_by=owner, **kw)
        return {
            'salon': make(name='Private client evening', code='SALON10', promo_type=Promotion.Type.PERCENTAGE, discount_value=10,
                          start_date=now - timedelta(days=4), end_date=now + timedelta(days=12), max_uses=40),
            'tier': make(name='Gold and Platinum appreciation', promo_type=Promotion.Type.TIERED,
                         start_date=now - timedelta(days=30), end_date=now + timedelta(days=60)),
            'spring': make(name='Spring preview', code='PREVIEW', promo_type=Promotion.Type.FIXED, discount_value=150,
                           start_date=now + timedelta(days=20), end_date=now + timedelta(days=34)),
            'summer': make(name='Summer silk week', code='SILK15', promo_type=Promotion.Type.PERCENTAGE, discount_value=15,
                           applies_to=Promotion.AppliesTo.CATEGORY, category='Accessories',
                           start_date=now - timedelta(days=150), end_date=now - timedelta(days=143), is_active=False),
        }

    def _sales(self, location, staff, variants, clients, promos, rng):
        sellers = [staff['cashier'], staff['sofia'], staff['owner']]
        # Lighter, cheaper pieces sell more often than high jewellery
        weights = [max(1.0, 12000 / float(v.retail_price)) for v in variants]
        today = timezone.localdate()
        orders = []

        def sale(when, items, client=None, promo=None):
            order = Order.objects.create(location=location, created_by=rng.choice(sellers), client=client,
                                         status=Order.Status.COMPLETED, total_amount=0)
            subtotal = Decimal('0')
            for variant, qty in items:
                OrderItem.objects.create(order=order, variant=variant, quantity=qty, unit_price=variant.retail_price)
                subtotal += variant.retail_price * qty
            discount = (subtotal * promo.discount_value / 100).quantize(Decimal('0.01')) if promo else Decimal('0')
            order.total_amount, order.total_discount = subtotal - discount, discount
            order.save(update_fields=['total_amount', 'total_discount'])
            if promo:
                PromotionUsage.objects.create(promotion=promo, client=client, order=order, discount_amount=discount)
                promo.used_count += 1
                promo.save(update_fields=['used_count'])
            Order.objects.filter(pk=order.pk).update(created_at=when)
            order.created_at = when
            orders.append(order)
            return order

        def at(day, hour, minute):
            return timezone.make_aware(datetime.combine(day, time(hour, minute)))

        for back in range(48, 0, -1):
            day = today - timedelta(days=back)
            if day.weekday() == 0:  # closed Mondays
                continue
            for _ in range(rng.choice([1, 2, 2, 3, 3, 4])):
                picks = rng.choices(variants, weights=weights, k=rng.choice([1, 1, 1, 2]))
                items = [(v, 1) for v in dict.fromkeys(picks)]
                client = rng.choice(clients) if rng.random() < 0.6 else None
                promo = promos['salon'] if back <= 4 and rng.random() < 0.3 else None
                sale(at(day, rng.randint(10, 18), rng.randint(0, 59)), items, client, promo)

        # Today, as of mid-afternoon, so the dashboard has a day in progress
        pick = lambda photo: self.by_photo[photo][0]
        sale(at(today, 10, 42), [(pick('hermes-silk-twill-scarf'), 1)], clients[0])
        sale(at(today, 11, 58), [(self.by_photo['cartier-love-bracelet'][1], 1)], clients[3], promos['salon'])
        sale(at(today, 13, 20), [(pick('loro-piana-cashmere-crewneck'), 1), (pick('prada-symbole-sunglasses'), 1)])
        sale(at(today, 14, 5), [(self.by_photo['louboutin-so-kate'][0], 1)], clients[2])
        sale(at(today, 15, 37), [(pick('saint-laurent-le-5-a-7'), 1)], clients[7])
        return orders

    def _returns(self, orders, staff, rng):
        recent = [o for o in orders if (timezone.now() - o.created_at).days <= 8 and o.items.count()]
        if len(recent) < 2:
            return
        # A refund on part of an order
        first = recent[0]
        item = first.items.first()
        ret = Return.objects.create(original_order=first, created_by=staff['cashier'], reason=Return.Reason.WRONG_SIZE, action=Return.Action.REFUND)
        ReturnItem.objects.create(return_process=ret, order_item=item, quantity=1, reason=Return.Reason.WRONG_SIZE)
        item.qty_returned = 1
        item.save(update_fields=['qty_returned'])
        first.status = Order.Status.FULLY_RETURNED if all(i.qty_returned >= i.quantity for i in first.items.all()) else Order.Status.PARTIALLY_RETURNED
        first.save(update_fields=['status'])

        # An exchange for a different size of the same piece, when one is in stock
        second = recent[1]
        item = second.items.first()
        swap = ProductVariant.objects.filter(product=item.variant.product, initial_quantity__gt=0).exclude(pk=item.variant.pk).first()
        if swap:
            replacement = Order.objects.create(type=Order.Type.EXCHANGE, parent_order=second, client=second.client,
                                               location=second.location, created_by=staff['sofia'],
                                               status=Order.Status.COMPLETED, total_amount=swap.retail_price)
            OrderItem.objects.create(order=replacement, variant=swap, quantity=1, unit_price=swap.retail_price)
            ret = Return.objects.create(original_order=second, created_by=staff['sofia'], reason=Return.Reason.WRONG_SIZE,
                                        action=Return.Action.EXCHANGE, replacement_order=replacement)
            ReturnItem.objects.create(return_process=ret, order_item=item, quantity=1, reason=Return.Reason.WRONG_SIZE)
            item.qty_returned = 1
            item.save(update_fields=['qty_returned'])
            second.status = Order.Status.FULLY_RETURNED if all(i.qty_returned >= i.quantity for i in second.items.all()) else Order.Status.PARTIALLY_RETURNED
            second.save(update_fields=['status'])
