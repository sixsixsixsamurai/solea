from decimal import Decimal
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from .models import Category, Recipe
from .views import _get_recommendations


class RecipeModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Vegan', slug='vegan')
        self.recipe = Recipe.objects.create(
            title='Avocado Salad',
            slug='avocado-salad',
            category=self.category,
            description='Fresh salad',
            instructions='Mix everything',
            cook_time=15,
            price=Decimal('10.00'),
        )

    def test_str(self):
        self.assertEqual(str(self.recipe), 'Avocado Salad')

    def test_cook_time_display(self):
        self.assertEqual(self.recipe.cook_time_display, '15 min')

    def test_nutrition_fields_null_by_default(self):
        self.assertIsNone(self.recipe.calories)
        self.assertIsNone(self.recipe.proteins)
        self.assertIsNone(self.recipe.fats)
        self.assertIsNone(self.recipe.carbohydrates)

    def test_nutrition_fields_save(self):
        self.recipe.calories = 420
        self.recipe.proteins = Decimal('8.5')
        self.recipe.fats = Decimal('22.0')
        self.recipe.carbohydrates = Decimal('48.0')
        self.recipe.save()
        self.recipe.refresh_from_db()
        self.assertEqual(self.recipe.calories, 420)
        self.assertEqual(self.recipe.proteins, Decimal('8.5'))

    def test_category_str(self):
        self.assertEqual(str(self.category), 'Vegan')


class MenuViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.vegan_cat = Category.objects.create(name='Vegan', slug='vegan')
        self.protein_cat = Category.objects.create(name='Protein', slug='protein')
        self.active_recipe = Recipe.objects.create(
            title='Avocado Tacos',
            slug='avocado-tacos',
            category=self.vegan_cat,
            description='desc',
            instructions='inst',
            cook_time=30,
            price=Decimal('12.00'),
        )
        self.inactive_recipe = Recipe.objects.create(
            title='Hidden Recipe',
            slug='hidden-recipe',
            description='desc',
            instructions='inst',
            cook_time=20,
            price=Decimal('8.00'),
            is_active=False,
        )
        self.protein_recipe = Recipe.objects.create(
            title='Chicken Bowl',
            slug='chicken-bowl',
            category=self.protein_cat,
            description='desc',
            instructions='inst',
            cook_time=25,
            price=Decimal('15.00'),
        )

    def test_menu_returns_200(self):
        response = self.client.get(reverse('recipes:menu'))
        self.assertEqual(response.status_code, 200)

    def test_only_active_recipes_shown(self):
        response = self.client.get(reverse('recipes:menu'))
        recipes = list(response.context['recipes'])
        self.assertIn(self.active_recipe, recipes)
        self.assertNotIn(self.inactive_recipe, recipes)

    def test_category_filter(self):
        response = self.client.get(reverse('recipes:menu') + '?category=vegan')
        recipes = list(response.context['recipes'])
        self.assertIn(self.active_recipe, recipes)
        self.assertNotIn(self.protein_recipe, recipes)

    def test_search_filter(self):
        response = self.client.get(reverse('recipes:menu') + '?search=avocado')
        recipes = list(response.context['recipes'])
        self.assertIn(self.active_recipe, recipes)
        self.assertNotIn(self.protein_recipe, recipes)

    def test_search_case_insensitive(self):
        response = self.client.get(reverse('recipes:menu') + '?search=AVOCADO')
        recipes = list(response.context['recipes'])
        self.assertIn(self.active_recipe, recipes)

    def test_search_no_results(self):
        response = self.client.get(reverse('recipes:menu') + '?search=nonexistentxyz')
        self.assertEqual(len(list(response.context['recipes'])), 0)


class RecipeDetailViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.recipe = Recipe.objects.create(
            title='Test Recipe',
            slug='test-recipe',
            description='A great dish',
            instructions='Cook it well',
            cook_time=30,
            price=Decimal('12.00'),
        )

    def test_detail_returns_200(self):
        response = self.client.get(reverse('recipes:detail', kwargs={'slug': 'test-recipe'}))
        self.assertEqual(response.status_code, 200)

    def test_detail_shows_title(self):
        response = self.client.get(reverse('recipes:detail', kwargs={'slug': 'test-recipe'}))
        self.assertContains(response, 'Test Recipe')

    def test_unknown_slug_returns_404(self):
        response = self.client.get(reverse('recipes:detail', kwargs={'slug': 'does-not-exist'}))
        self.assertEqual(response.status_code, 404)

    def test_inactive_recipe_returns_404(self):
        self.recipe.is_active = False
        self.recipe.save()
        response = self.client.get(reverse('recipes:detail', kwargs={'slug': 'test-recipe'}))
        self.assertEqual(response.status_code, 404)


class RecommendationAlgorithmTest(TestCase):
    """Tests for _get_recommendations() — the core personalisation algorithm."""

    def setUp(self):
        from apps.orders.models import Order, OrderItem

        self.Order = Order
        self.OrderItem = OrderItem
        self.factory = RequestFactory()

        self.vegan_cat = Category.objects.create(name='Vegan', slug='vegan')
        self.protein_cat = Category.objects.create(name='Protein', slug='protein')

        self.vegan_recipes = [
            Recipe.objects.create(
                title=f'Vegan Recipe {i}', slug=f'vegan-recipe-{i}',
                category=self.vegan_cat, description='desc', instructions='inst',
                cook_time=20, price=Decimal('10.00'),
            )
            for i in range(3)
        ]
        self.protein_recipes = [
            Recipe.objects.create(
                title=f'Protein Recipe {i}', slug=f'protein-recipe-{i}',
                category=self.protein_cat, description='desc', instructions='inst',
                cook_time=25, price=Decimal('12.00'),
            )
            for i in range(3)
        ]

        self.user = get_user_model().objects.create_user(
            username='testuser', password='testpass'
        )

    def _make_request(self, user=None):
        request = self.factory.get('/')
        request.user = user if user else AnonymousUser()
        return request

    def _make_delivered_order(self, user, recipe, quantity=1):
        order = self.Order.objects.create(user=user, status=self.Order.Status.DELIVERED)
        self.OrderItem.objects.create(
            order=order, recipe=recipe,
            quantity=quantity, unit_price=recipe.price,
        )
        return order

    def test_cold_start_returns_vegan_and_protein_fallback(self):
        """Authenticated user with zero order history gets a vegan+protein mix."""
        request = self._make_request(user=self.user)

        result = _get_recommendations(request, count=4)

        self.assertLessEqual(len(result), 4)
        self.assertGreater(len(result), 0)
        category_slugs = {r.category.slug for r in result}
        self.assertTrue(
            category_slugs.issubset({'vegan', 'protein'}),
            f'Cold-start returned unexpected categories: {category_slugs}',
        )

    def test_vegan_only_history_recommends_vegan(self):
        """User whose every past order was vegan should receive only vegan recipes."""
        for recipe in self.vegan_recipes:
            self._make_delivered_order(self.user, recipe)

        request = self._make_request(user=self.user)
        result = _get_recommendations(request, count=4)

        self.assertGreater(len(result), 0)
        for recipe in result:
            self.assertEqual(
                recipe.category.slug, 'vegan',
                f'Expected vegan recommendation, got: {recipe.category.slug}',
            )

    def test_mixed_history_returns_both_categories(self):
        """User with 2 vegan orders and 1 protein order gets recs from both categories."""
        for recipe in self.vegan_recipes[:2]:
            self._make_delivered_order(self.user, recipe)
        self._make_delivered_order(self.user, self.protein_recipes[0])

        request = self._make_request(user=self.user)
        result = _get_recommendations(request, count=4)

        self.assertGreater(len(result), 0)
        self.assertLessEqual(len(result), 4)
        category_slugs = {r.category.slug for r in result}
        self.assertIn('vegan', category_slugs)
        self.assertIn('protein', category_slugs)
