from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='recipes')
    description = models.TextField()
    instructions = models.TextField()
    cook_time = models.PositiveIntegerField(help_text='Time in minutes')
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.ImageField(upload_to='recipes/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    @property
    def cook_time_display(self):
        return f'{self.cook_time} min'


class Ingredient(models.Model):
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='ingredients')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name='recipe_ingredients')
    quantity = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.quantity} {self.ingredient.name}'
