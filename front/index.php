<?php
$page = $_GET['page'] ?? 'main';

$allowedPages = ['main', 'menu', 'sustainability', 'partners', 'recipe'];

if (!in_array($page, $allowedPages)) {
    $page = 'main';
}
?>

<!DOCTYPE html>
<html>
<head> 
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Solea</title>

    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Rowdies:wght@300;400;700&family=Varela+Round&display=swap" rel="stylesheet">

    <link rel="icon" type="image/png" href="/picture_main/SoleaIcon.svg">
    <link rel="stylesheet" href="main.css">
    <link rel="stylesheet" href="menu.css">
</head>

<body>

<?php require 'header.php'; ?>

<?php require $page . '.php'; ?>

<?php require 'modals.php'; ?>

<?php require 'footer.php'; ?>


</body>
</html>