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
// NOTE: after switching to MongoDB we expect $conn to be the array returned
// by connectionToDB(): ['manager' => MongoDB\Driver\Manager, 'db' => 'dbname']

function createUser($conn, $login, $mdp_hache) {
    // Crée un nouvel utilisateur dans la collection `utilisateurs`
    $manager = $conn['manager'];
    $db = $conn['db'];

    $bulk = new MongoDB\Driver\BulkWrite;
    $user = ['login' => $login, 'mdp' => $mdp_hache];
    $bulk->insert($user);

    $namespace = $db . '.utilisateurs';

    try {
        $manager->executeBulkWrite($namespace, $bulk);
        return true;
    } catch (Exception $e) {
        return false;
    }
}

function getUser($conn, $login) {
    // Récupère le document utilisateur { login, mdp, ... } depuis la collection `utilisateurs`
    $manager = $conn['manager'];
    $db = $conn['db'];

    $filter = ['login' => $login];
    $options = ['limit' => 1];

    $query = new MongoDB\Driver\Query($filter, $options);
    $namespace = $db . '.utilisateurs';

    $rows = $manager->executeQuery($namespace, $query);
    $result = current($rows->toArray());

    if ($result) {
        // Retourne un tableau associatif pour compatibilité (mdp accessible par ['mdp'])
        return [
            'login' => $result->login ?? null,
            'mdp' => $result->mdp ?? null,
        ];
    }
    return null;
}

function check_user_exists($conn, $login) {
    // Vérifie si un utilisateur existe dans la collection `utilisateurs`
    $manager = $conn['manager'];
    $db = $conn['db'];

    $filter = ['login' => $login];
    $options = ['limit' => 1, 'projection' => ['_id' => 1]];

    $query = new MongoDB\Driver\Query($filter, $options);
    $namespace = $db . '.utilisateurs';

    $rows = $manager->executeQuery($namespace, $query);
    $arr = $rows->toArray();
    return count($arr) > 0;
}

function create_user($conn, $login, $mdp_hache) {
    // Insère un nouveau document utilisateur dans la collection `utilisateurs`
    $manager = $conn['manager'];
    $db = $conn['db'];

    $bulk = new MongoDB\Driver\BulkWrite();
    $doc = [
        'login' => $login,
        'mdp' => $mdp_hache,
        'created_at' => new MongoDB\BSON\UTCDateTime()
    ];

    $insertedId = $bulk->insert($doc);
    try {
        $result = $manager->executeBulkWrite($db . '.utilisateurs', $bulk);
        return $insertedId; // BSON\ObjectId ou valeur insérée
    } catch (MongoDB\Driver\Exception\BulkWriteException $e) {
        // Duplicate key or write error
        return false;
    } catch (Exception $e) {
        return false;
    }
}
?>