import django.db.models.deletion
from django.db import migrations, models


def migrate_ingredients_forward(apps, schema_editor):
    """
    Для каждой строки в старой таблице RecipeIngredient (бывшей Ingredient):
    - get_or_create Ingredient по name
    - проставить FK ingredient
    """
    RecipeIngredient = apps.get_model('recipes', 'RecipeIngredient')
    Ingredient = apps.get_model('recipes', 'Ingredient')

    for ri in RecipeIngredient.objects.all():
        ingredient, _ = Ingredient.objects.get_or_create(name=ri.name)
        ri.ingredient = ingredient
        ri.save()


def migrate_ingredients_backward(apps, schema_editor):
    """
    Обратная миграция: копируем name из ingredient обратно в поле name RecipeIngredient.
    """
    RecipeIngredient = apps.get_model('recipes', 'RecipeIngredient')
    for ri in RecipeIngredient.objects.select_related('ingredient').all():
        ri.name = ri.ingredient.name
        ri.save()


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0001_initial'),
    ]

    operations = [
        # 1. Переименовываем модель Ingredient → RecipeIngredient
        #    Django переименует таблицу recipes_ingredient → recipes_recipeingredient
        migrations.RenameModel(
            old_name='Ingredient',
            new_name='RecipeIngredient',
        ),

        # 2. Создаём новую таблицу recipes_ingredient — справочник ингредиентов
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True,
                                           serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True)),
            ],
        ),

        # 3. Добавляем FK ingredient в RecipeIngredient (пока nullable — нужно для data migration)
        migrations.AddField(
            model_name='RecipeIngredient',
            name='ingredient',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='recipe_ingredients',
                to='recipes.ingredient',
            ),
        ),

        # 4. Переносим данные
        migrations.RunPython(
            migrate_ingredients_forward,
            migrate_ingredients_backward,
        ),

        # 5. Делаем FK обязательным
        migrations.AlterField(
            model_name='RecipeIngredient',
            name='ingredient',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='recipe_ingredients',
                to='recipes.ingredient',
            ),
        ),

        # 6. Убираем поле name из RecipeIngredient (теперь оно в Ingredient)
        migrations.RemoveField(
            model_name='RecipeIngredient',
            name='name',
        ),
    ]
