<?php
function connectionToDB() {
<<<<<<< HEAD
    $host = getenv('MONGO_HOST') ?: 'mongo_database';
=======
    $host = getenv('MONGO_HOST') ?: 'mongo';
>>>>>>> 5e5ec9e03094316b728794fabadef7886e83f63d
    $port = getenv('MONGO_PORT') ?: '27017';
    $db   = getenv('MONGO_DB') ?: 'archiDistriRestaurants';
    $uri  = getenv('MONGO_URI') ?: "mongodb://{$host}:{$port}";

    try {
        $manager = new MongoDB\Driver\Manager($uri);
        return ['manager' => $manager, 'db' => $db];
    } catch (Exception $e) {
        die('<p>Erreur de connexion à MongoDB : ' . $e->getMessage() . '</p>');
    }
}
?>