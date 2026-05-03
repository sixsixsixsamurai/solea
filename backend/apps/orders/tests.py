from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.recipes.models import Recipe, Category
from .models import Order, OrderItem

User = get_user_model()


class OrderModelTest(TestCase):
    def setUp(self):
        self.recipe = Recipe.objects.create(
            title='Bowl', slug='bowl', description='d', instructions='i',
            cook_time=20, price=Decimal('10.00'),
        )
        self.order = Order.objects.create()

    def test_order_str(self):
        self.assertIn('pending', str(self.order).lower())

    def test_subtotal_property(self):
        item = OrderItem(recipe=self.recipe, quantity=3, unit_price=Decimal('5.00'))
        self.assertEqual(item.subtotal, Decimal('15.00'))

    def test_recalculate_total(self):
        OrderItem.objects.create(
            order=self.order, recipe=self.recipe, quantity=2, unit_price=Decimal('10.00')
        )
        self.order.recalculate_total()
        self.order.refresh_from_db()
        self.assertEqual(self.order.total_price, Decimal('20.00'))

    def test_recalculate_total_multiple_items(self):
        recipe2 = Recipe.objects.create(
            title='Salad', slug='salad', description='d', instructions='i',
            cook_time=10, price=Decimal('8.00'),
        )
        OrderItem.objects.create(order=self.order, recipe=self.recipe, quantity=2, unit_price=Decimal('10.00'))
        OrderItem.objects.create(order=self.order, recipe=recipe2, quantity=1, unit_price=Decimal('8.00'))
        self.order.recalculate_total()
        self.order.refresh_from_db()
        self.assertEqual(self.order.total_price, Decimal('28.00'))


class CartAddTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.recipe = Recipe.objects.create(
            title='Bowl', slug='bowl', description='d', instructions='i',
            cook_time=20, price=Decimal('12.00'),
        )

    def test_guest_can_add_to_cart(self):
        self.client.post(reverse('orders:add', kwargs={'recipe_id': self.recipe.id}))
        self.assertEqual(Order.objects.filter(status=Order.Status.PENDING).count(), 1)

    def test_adding_same_item_increments_quantity(self):
        self.client.post(reverse('orders:add', kwargs={'recipe_id': self.recipe.id}))
        self.client.post(reverse('orders:add', kwargs={'recipe_id': self.recipe.id}))
        order = Order.objects.filter(status=Order.Status.PENDING).first()
        self.assertEqual(order.items.first().quantity, 2)

    def test_add_requires_post(self):
        response = self.client.get(reverse('orders:add', kwargs={'recipe_id': self.recipe.id}))
        self.assertEqual(response.status_code, 405)

    def test_add_inactive_recipe_returns_404(self):
        self.recipe.is_active = False
        self.recipe.save()
        response = self.client.post(reverse('orders:add', kwargs={'recipe_id': self.recipe.id}))
        self.assertEqual(response.status_code, 404)


class CartRemoveSecurityTest(TestCase):
    """Проверяет что пользователь не может удалить чужие товары из корзины."""

    def setUp(self):
        self.user = User.objects.create_user(username='user1', password='pass12345')
        self.other_user = User.objects.create_user(username='user2', password='pass12345')
        self.recipe = Recipe.objects.create(
            title='Bowl', slug='bowl', description='d', instructions='i',
            cook_time=20, price=Decimal('12.00'),
        )

    def test_user_can_remove_own_item(self):
        self.client.login(username='user1', password='pass12345')
        order = Order.objects.create(user=self.user, status=Order.Status.PENDING)
        item = OrderItem.objects.create(order=order, recipe=self.recipe, quantity=1, unit_price=Decimal('12.00'))
        self.client.post(reverse('orders:remove', kwargs={'item_id': item.id}))
        self.assertFalse(OrderItem.objects.filter(pk=item.id).exists())

    def test_user_cannot_remove_other_users_item(self):
        self.client.login(username='user1', password='pass12345')
        other_order = Order.objects.create(user=self.other_user, status=Order.Status.PENDING)
        other_item = OrderItem.objects.create(
            order=other_order, recipe=self.recipe, quantity=1, unit_price=Decimal('12.00')
        )
        response = self.client.post(reverse('orders:remove', kwargs={'item_id': other_item.id}))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(OrderItem.objects.filter(pk=other_item.id).exists())


class PlaceOrderTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='pass12345')
        self.recipe = Recipe.objects.create(
            title='Bowl', slug='bowl', description='d', instructions='i',
            cook_time=20, price=Decimal('12.00'),
        )

    def test_place_order_requires_login(self):
        response = self.client.post(reverse('orders:place_order'))
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['error'], 'login_required')

    def test_place_order_empty_cart_returns_400(self):
        self.client.login(username='testuser', password='pass12345')
        response = self.client.post(reverse('orders:place_order'))
        self.assertEqual(response.status_code, 400)

    def test_place_order_incomplete_address_returns_400(self):
        self.client.login(username='testuser', password='pass12345')
        order = Order.objects.create(user=self.user, status=Order.Status.PENDING)
        OrderItem.objects.create(order=order, recipe=self.recipe, quantity=1, unit_price=Decimal('12.00'))
        response = self.client.post(reverse('orders:place_order'), {'city': 'Kyiv'})
        self.assertEqual(response.status_code, 400)

    def test_place_order_success(self):
        self.client.login(username='testuser', password='pass12345')
        order = Order.objects.create(user=self.user, status=Order.Status.PENDING)
        OrderItem.objects.create(order=order, recipe=self.recipe, quantity=1, unit_price=Decimal('12.00'))
        response = self.client.post(reverse('orders:place_order'), {
            'city': 'Kyiv', 'street': 'Main St', 'house': '1'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
