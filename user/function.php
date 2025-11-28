<?php
function deliver_response($status, $status_message, $data = null)
{
    // Définit les en-têtes HTTP et le type de contenu
    header("HTTP/1.1 $status $status_message");
    header("Content-Type: application/json");

    // Crée et envoie la réponse JSON
    $response = [
        'status' => $status,
        'status_message' => $status_message,
        'data' => $data
    ];

    echo json_encode($response);
}

function getUser($pdo, $login) {
    // Récupère le mot de passe de l'utilisateur correspondant au login
    $stmt = $pdo->prepare("SELECT mdp FROM utilisateurs WHERE login = :login");
    $stmt->execute([':login' => $login]);
    return $stmt->fetch(PDO::FETCH_ASSOC);
}

function check_user_exists($pdo, $login) {
    // Vérifie si un utilisateur existe dans la base de données
    $stmt = $pdo->prepare("SELECT COUNT(*) FROM utilisateurs WHERE login = :login");
    $stmt->execute([':login' => $login]);
    $count = $stmt->fetchColumn();
    return $count > 0;
}
?>