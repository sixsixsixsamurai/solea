<?php
$id = $_GET['id'] ?? null;

$recipes = [
    1 => [
        "title" => "Avocado Tacos",
        "time" => "30 min",
        "description" => "Where recipes become moments, and ingredients arrive with purpose.",
        "ingredients" => 6,
        "price" => 30,
        "image" => "/picture_menu/vegan/avocadotaco.jpg",
        "category" => "vegan",
        "actIngredients" => "avocado, tortilia, mayoneisse sous, brockoli, cabbage, hope",
        "instructions" => "very very long text with instructions on how acually cook it, taco"
    ],
    2 => [
        "title" => "Vegan Bowl",
        "time" => "25 min",
        "description" => "Healthy and colorful vegan bowl full of nutrients.",
        "ingredients" => 8,
        "price" => 25,
        "image" => "/picture_menu/vegan/avocadotaco.jpg",
        "category" => "vegan",
        "actIngredients" => "avocado, tortilia, mayoneisse sous, brockoli, cabbage, hope, vegans, peace",
        "instructions" => "very very long text with instructions on how acually cook it"
    ]
];

$recipe = $recipes[$id] ?? null;
?>

<?php if ($recipe): ?>

<div class="recipe-page">

    <div class="recipe-top">
        <img src="<?= $recipe['image'] ?>" alt="recipe">

        <div class="recipe-info">
            <h2><?= $recipe['title'] ?></h2>

            <div class="time"><?= $recipe['time'] ?></div>

            <div class="recipe-meta">
                <span>Ingredients: <?= $recipe['actIngredients'] ?></span>
                <span>Category: <?= $recipe['category'] ?></span>
            </div>

            <p><?= $recipe['description'] ?></p>
<div class="inLine">
            <div class="recipe-price">
                <?= $recipe['price'] ?>$
            </div>

            <div class="buttonCart">
                <h4>Add to cart</h4>
            </div>
</div>
        </div>
    </div>

    <div class="instructions"><?= $recipe['instructions'] ?></div>


</div>

<?php else: ?>

<p>Recipe not found</p>

<?php endif; ?>