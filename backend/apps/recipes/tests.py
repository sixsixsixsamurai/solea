from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from .models import Category, Recipe


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
