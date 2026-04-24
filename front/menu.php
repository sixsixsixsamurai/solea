<?php
$recipes = [
    [
        "id" => 1,
        "title" => "Avocado Tacos",
        "time" => "30 min",
        "description" => "Where recipes become moments, and ingredients arrive with purpose.",
        "ingredients" => ["Avocado", "Tortilla", "Lime", "Cilantro", "Onion", "Jalapeño"],
        "price" => 30,
        "image" => "/picture_menu/vegan/avocadotaco.jpg",
        "category" => "vegan"
    ],
    [
        "id" => 1,
        "title" => "Avocado Tacos",
        "time" => "30 min",
        "description" => "Where recipes become moments, and ingredients arrive with purpose.",
        "ingredients" => ["Avocado", "Tortilla", "Lime", "Cilantro", "Onion", "Jalapeño"],
        "price" => 30,
        "image" => "/picture_menu/vegan/avocadotaco.jpg",
        "category" => "vegan"
    ],
    [
        "id" => 1,
        "title" => "Avocado Tacos",
        "time" => "30 min",
        "description" => "Where recipes become moments, and ingredients arrive with purpose.",
        "ingredients" => ["Avocado", "Tortilla", "Lime", "Cilantro", "Onion", "Jalapeño"],
        "price" => 30,
        "image" => "/picture_menu/vegan/avocadotaco.jpg",
        "category" => "vegan"
    ],
    [
        "id" => 1,
        "title" => "Avocado Tacos",
        "time" => "30 min",
        "description" => "Where recipes become moments, and ingredients arrive with purpose.",
        "ingredients" => ["Avocado", "Tortilla", "Lime", "Cilantro", "Onion", "Jalapeño"],
        "price" => 30,
        "image" => "/picture_menu/vegan/avocadotaco.jpg",
        "category" => "vegan"
    ],
    [
        "id" => 1,
        "title" => "Avocado Tacos",
        "time" => "30 min",
        "description" => "Where recipes become moments, and ingredients arrive with purpose.",
        "ingredients" => ["Avocado", "Tortilla", "Lime", "Cilantro", "Onion", "Jalapeño"],
        "price" => 30,
        "image" => "/picture_menu/vegan/avocadotaco.jpg",
        "category" => "vegan"
    ],
];
?>


<div class="big">

<div class="elements">
    <div class="buttonSort">
    <img src="/picture_menu/sort.svg">
    </div>

    <div class="search">
    <img src="/picture_menu/search.svg" alt="search" class="search-icon">
        <input
        type="text"
        placeholder="Search recipes..."
        class="search-input"
        >
    </div>
</div>

<div class="cards-container">

<?php foreach ($recipes as $recipe): ?>

<div class="card" data-link="?page=recipe&id=<?= $recipe['id'] ?>">
    <img src="<?= $recipe['image'] ?>" alt="<?= $recipe['title'] ?>">

    <div class="card-content">
        <h3><?= $recipe['title'] ?></h3>

        <div class="time">
            <span><?= $recipe['time'] ?></span>
        </div>

        <p><?= $recipe['description'] ?></p>

        <div class="decor"></div>

        <div class="card-middle">
            <div class="ingredients-block">
                <span class="ingredients-label">Ingredients</span>
                <div class="ingredients-list">
                    <?php
                    $ingredients = $recipe['ingredients'];
                    $shown = array_slice($ingredients, 0, 4);
                    foreach ($shown as $ing):
                    ?>
                        <span class="ingredient-item"><?= $ing ?></span>
                    <?php endforeach; ?>
                    <?php if (count($ingredients) > 4): ?>
                        <a class="more-link" href="?page=recipe&id=<?= $recipe['id'] ?>">more</a>
                    <?php endif; ?>
                </div>
            </div>
            <span class="ammount"><?= count($recipe['ingredients']) ?></span>
        </div>

        <div class="decor"></div>

        <div class="card-footer">
            <div class="price"><?= $recipe['price'] ?>$</div>

            <div class="add-btn" onclick="event.stopPropagation()">
                <img src="/picture_menu/addtobasket.svg" alt="add">
            </div>
        </div>

    </div>
</div>

<?php endforeach; ?>

</div>
</div>
