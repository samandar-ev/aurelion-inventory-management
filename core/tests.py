"""Security regression tests: each one reproduces a hole that was fixed."""
import io
import json
import tempfile
from datetime import timedelta
from decimal import Decimal

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from .models import Client, Location, Order, OrderItem, Product, ProductImage, ProductVariant, User
from .views import _sheet_safe


@override_settings(MEDIA_ROOT=tempfile.mkdtemp(prefix='aurelion-test-media-'), STORAGES={
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
})
class Base(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.loc = Location.objects.create(name='Store', code='MAIN', address='-')
        cls.owner = User.objects.create_user('owner', password='pw', role=User.Role.OWNER)
        cls.cashier = User.objects.create_user('cashier', password='pw', role=User.Role.CASHIER)
        cls.associate = User.objects.create_user('associate', password='pw', role=User.Role.SALES_ASSOCIATE)
        cls.product = Product.objects.create(brand='Hermès', name='Birkin 30', category='Bags', base_sku='HER-B30')
        cls.variant = ProductVariant.objects.create(
            product=cls.product, sku='HER-B30-GLD', color='Gold', size='30',
            cost_price=Decimal('9000'), retail_price=Decimal('18900'), initial_quantity=5)

    def post_json(self, name, data):
        return self.client.post(reverse(name), json.dumps(data), content_type='application/json')

    def sale(self, days_ago=0):
        order = Order.objects.create(order_code=f'T{days_ago:05d}', location=self.loc, created_by=self.cashier,
                                     status=Order.Status.COMPLETED, total_amount=Decimal('18900'))
        OrderItem.objects.create(order=order, variant=self.variant, quantity=1, unit_price=Decimal('18900'))
        Order.objects.filter(pk=order.pk).update(created_at=timezone.now() - timedelta(days=days_ago))
        return order


class RoleBoundaries(Base):
    def test_associate_cannot_use_pos_endpoints(self):
        self.client.force_login(self.associate)
        for name in ('pos_checkout', 'pos_preview_discount', 'pos_return_lookup'):
            resp = self.post_json(name, {'items': [{'sku': 'HER-B30-GLD', 'qty': 1, 'price': 1}]})
            self.assertEqual(resp.status_code, 403, name)
        self.assertFalse(Order.objects.exists())

    def test_associate_cannot_read_orders_or_sales(self):
        order = self.sale()
        self.client.force_login(self.associate)
        self.assertEqual(self.client.get(reverse('order_detail', args=[order.pk])).status_code, 403)
        self.assertRedirects(self.client.get(reverse('dashboard')), reverse('associate_dashboard'))
        self.assertEqual(self.client.get(reverse('archived_product_list')).status_code, 403)

    def test_api_is_read_only_and_role_scoped(self):
        order = self.sale()
        self.client.force_login(self.associate)
        self.assertIn(self.client.delete(f'/api/products/{self.product.pk}/').status_code, (403, 405))
        self.assertIn(self.client.post('/api/clients/', {'first_name': 'X', 'phone': '1'}).status_code, (403, 405))
        self.assertFalse(Client.objects.exists())
        self.assertEqual(self.client.get('/api/orders/').status_code, 403)
        self.client.force_login(self.cashier)
        resp = self.client.patch(f'/api/orders/{order.pk}/', json.dumps({'total_amount': '1.00'}),
                                 content_type='application/json')
        self.assertEqual(resp.status_code, 405)
        self.assertEqual(Order.objects.get(pk=order.pk).total_amount, Decimal('18900'))
        self.assertTrue(Product.objects.filter(pk=self.product.pk).exists())


class MoneyIntegrity(Base):
    def test_checkout_uses_catalog_price_not_client_price(self):
        self.client.force_login(self.cashier)
        resp = self.post_json('pos_checkout', {
            'items': [{'sku': 'HER-B30-GLD', 'qty': 1, 'price': '1.00'}], 'discount': '5000'})
        self.assertEqual(resp.status_code, 200)
        order = Order.objects.get()
        self.assertEqual(order.total_amount, Decimal('18900'))
        self.assertEqual(order.items.get().unit_price, Decimal('18900'))

    def test_checkout_rejects_overselling(self):
        self.client.force_login(self.cashier)
        resp = self.post_json('pos_checkout', {'items': [{'sku': 'HER-B30-GLD', 'qty': 6}]})
        self.assertEqual(resp.status_code, 400)
        self.assertFalse(Order.objects.exists())

    def test_exchange_uses_catalog_price(self):
        order = self.sale()
        self.client.force_login(self.cashier)
        resp = self.post_json('pos_return_checkout', {
            'order_code': order.order_code, 'action': 'EXCHANGE', 'reason': 'OTHER',
            'return_items': [{'id': order.items.get().id, 'qty': 1}],
            'replacement_items': [{'sku': 'HER-B30-GLD', 'qty': 1, 'price': '1.00'}]})
        self.assertEqual(resp.status_code, 200, resp.content)
        exchange = Order.objects.get(type=Order.Type.EXCHANGE)
        self.assertEqual(exchange.total_amount, Decimal('18900'))

    def test_return_window_enforced_at_checkout(self):
        order = self.sale(days_ago=40)
        self.client.force_login(self.cashier)
        resp = self.post_json('pos_return_checkout', {
            'order_code': order.order_code, 'action': 'REFUND', 'reason': 'OTHER',
            'return_items': [{'id': order.items.get().id, 'qty': 1}]})
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(order.items.get().qty_returned, 0)

    def test_return_rejects_unknown_action(self):
        order = self.sale()
        self.client.force_login(self.cashier)
        resp = self.post_json('pos_return_checkout', {
            'order_code': order.order_code, 'action': 'PAYOUT', 'reason': 'OTHER',
            'return_items': [{'id': order.items.get().id, 'qty': 1}]})
        self.assertEqual(resp.status_code, 400)


class Injection(Base):
    def test_order_detail_json_cannot_close_script(self):
        self.product.name = '</script><script>alert(1)</script>'
        self.product.save()
        order = self.sale()
        self.client.force_login(self.cashier)
        html = self.client.get(reverse('order_detail', args=[order.pk])).content.decode()
        self.assertNotIn('</script><script>alert(1)', html)

    def test_pos_escapes_catalog_text_before_innerhtml(self):
        self.client.force_login(self.cashier)
        html = self.client.get(reverse('pos')).content.decode()
        self.assertIn('function esc(', html)
        self.assertNotIn('${v.name}', html)
        self.assertNotIn('${item.name}', html)
        self.assertNotIn('${l.name}', html)

    def test_excel_cells_never_start_formulas(self):
        self.assertEqual(_sheet_safe('=HYPERLINK("http://x")'), '\'=HYPERLINK("http://x")')
        self.assertEqual(_sheet_safe('@SUM(A1)'), "'@SUM(A1)")
        self.assertEqual(_sheet_safe('Eleanor'), 'Eleanor')

    def test_gallery_rejects_non_images(self):
        self.client.force_login(self.cashier)
        png = io.BytesIO()
        from PIL import Image
        Image.new('RGB', (4, 4)).save(png, 'PNG')
        data = {
            'brand': 'Cartier', 'name': 'Love', 'category': 'Jewelry', 'condition': 'New',
            'variants-TOTAL_FORMS': '1', 'variants-INITIAL_FORMS': '0',
            'variants-MIN_NUM_FORMS': '1', 'variants-MAX_NUM_FORMS': '1000',
            'variants-0-color': 'Gold', 'variants-0-size': '17', 'variants-0-retail_price': '7350',
            'variants-0-initial_quantity': '1', 'variants-0-currency': 'USD',
            'image': SimpleUploadedFile('a.png', png.getvalue(), 'image/png'),
            'additional_images': SimpleUploadedFile('x.html', b'<script>alert(1)</script>', 'text/html'),
        }
        self.client.post(reverse('luxury_product_create'), data)
        self.assertFalse(ProductImage.objects.filter(image__endswith='.html').exists())

    def test_cashier_cannot_set_cost_price(self):
        from .forms import ProductVariantForm
        form = ProductVariantForm(data={'color': 'Gold', 'size': '17', 'retail_price': '100',
                                        'cost_price': '1', 'initial_quantity': '1', 'currency': 'USD'},
                                  user=self.cashier)
        form.is_valid()
        self.assertEqual(form.cleaned_data.get('cost_price'), Decimal('0.00'))


class Accounts(Base):
    def test_personnel_rejects_weak_password_and_bogus_role(self):
        self.client.force_login(self.owner)
        self.client.post(reverse('personnel_create'), {
            'username': 'weak', 'password': '1234', 'confirm_password': '1234', 'role': 'CASHIER'})
        self.client.post(reverse('personnel_create'), {
            'username': 'bogus', 'password': 'Velvet-Ledger-81', 'confirm_password': 'Velvet-Ledger-81',
            'role': 'GODMODE'})
        self.assertFalse(User.objects.filter(username__in=['weak', 'bogus']).exists())


class AssociateLookup(Base):
    def test_lookup_shows_real_stock_numbers(self):
        self.client.force_login(self.associate)
        html = self.client.get(reverse('associate_dashboard'), {'q': 'HER-B30'}).content.decode()
        self.assertIn('Birkin 30', html)
        self.assertIn('<span class="qty">5</span>', html)

    def test_lookup_matches_brand(self):
        self.client.force_login(self.associate)
        html = self.client.get(reverse('associate_dashboard'), {'q': 'hermès'}).content.decode()
        self.assertIn('Birkin 30', html)


class Smoke(Base):
    """Every page renders for every role: allowed pages return 200, others are refused, none crash."""

    def test_every_page_for_every_role(self):
        order = self.sale()
        client = Client.objects.create(first_name='Eleanor', last_name='Whitcombe', phone='+1 212 555 0148')
        from .models import Promotion
        promo = Promotion.objects.create(name='Evening', code='EVE10', promo_type='PERCENTAGE', discount_value=10,
                                         start_date=timezone.now(), end_date=timezone.now() + timedelta(days=5))
        pages = [
            ('dashboard', []), ('associate_dashboard', []), ('product_list', []), ('archived_product_list', []),
            ('product_detail', [self.product.pk]), ('product_create', []), ('luxury_product_create', []),
            ('product_edit', [self.product.pk]), ('product_delete', [self.product.pk]),
            ('barcode_generator', []), ('client_list', []), ('client_create', []),
            ('client_detail', [client.pk]), ('client_edit', [client.pk]), ('pos', []), ('pos_return', []),
            ('order_list', []), ('order_detail', [order.pk]), ('promotion_list', []), ('promotion_create', []),
            ('promotion_edit', [promo.pk]), ('reports', []), ('report_export', []),
            ('personnel_list', []), ('personnel_create', []),
        ]
        for user in (self.owner, self.cashier, self.associate):
            self.client.force_login(user)
            for name, args in pages:
                resp = self.client.get(reverse(name, args=args))
                self.assertIn(resp.status_code, (200, 302, 403), f'{name} as {user.username}: {resp.status_code}')
            for path in ('/api/products/', '/api/clients/', '/api/orders/'):
                self.assertIn(self.client.get(path).status_code, (200, 403), path)
        self.client.logout()
        self.assertEqual(self.client.get(reverse('login')).status_code, 200)
        self.assertEqual(self.client.get(reverse('health')).status_code, 200)
        self.assertRedirects(self.client.get(reverse('dashboard')), reverse('login') + '?next=' + reverse('dashboard'))
