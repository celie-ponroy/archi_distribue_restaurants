<?php
function connectionToDB() {
    // Informations de connexion à la base de données
    $host = "mysql-immolink.alwaysdata.net";
    $dbname = "immolink_bdd";
    $username = "immolink";
    $password = '$iutinfo';

    try {
        // Création de la connexion PDO avec gestion des erreurs
        $pdo = new PDO('mysql:host=' . $host . ';dbname=' . $dbname . ';charset=utf8mb4', $username, $password);
        $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
        return $pdo;
    } catch (PDOException $e) {
        // Affiche une erreur et arrête l'exécution en cas d'échec de connexion
        die("<p>Erreur de connexion à la base de données : " . $e->getMessage() . "</p>");
    }
}
?>