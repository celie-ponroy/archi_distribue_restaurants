<?php
require_once 'jwt_utils.php';
require_once 'connectionbd.php';
require_once 'function.php';

$method = $_SERVER['REQUEST_METHOD'];
$input = json_decode(file_get_contents('php://input'), true);
$conn = connectionToDB();
$secret = getenv('JWT_SECRET') ?: 'coucou_je_suis_secret';

// Helper: require valid token and return payload array
function require_token_payload($secret) {
    if (!get_bearer_token()) {
        deliver_response(401, "Token manquant");
        exit;
    }
    $token = get_bearer_token();
    if (!is_jwt_valid($token, $secret)) {
        deliver_response(401, "Token invalide");
        exit;
    }
    $payload = decode_jwt_payload($token);
    if (!$payload) {
        deliver_response(401, "Token invalide (payload)");
        exit;
    }
    return $payload;
}

function has_bearer_token() {
    $header = get_authorization_header();
    if (!empty($header) && preg_match('/Bearer\s(\S+)/', $header, $matches)) {
        return true;
    }
    return false;
}

switch ($method) {
    case 'GET':
        // list or get a user
        $payload = require_token_payload($secret);
        $isAdmin = isset($payload['admin']) && $payload['admin'];

        // Query params
        $login = $_GET['login'] ?? null;
        $all = isset($_GET['all']);

        if ($all) {
            if (!$isAdmin) {
                deliver_response(403, 'Opération réservée aux admins');
                exit;
            }
            // return all users (without passwords)
            $manager = $conn['manager'];
            $db = $conn['db'];
            $query = new MongoDB\Driver\Query([]);
            $rows = $manager->executeQuery($db . '.user', $query);
            $out = [];
            foreach ($rows as $r) {
                $out[] = ['login' => $r->login ?? null, 'admin' => isset($r->admin) ? (bool)$r->admin : false];
            }
            deliver_response(200, 'OK', $out);
            exit;
        }

        if ($login) {
            // can consult if admin or if it's their own account
            if (!$isAdmin && ($payload['login'] ?? '') !== $login) {
                deliver_response(403, 'Accès refusé');
                exit;
            }
            $user = getUser($conn, $login);
            if (!$user) {
                deliver_response(404, 'Utilisateur non trouvé');
                exit;
            }
            // don't expose hashed password
            unset($user['mdp']);
            deliver_response(200, 'OK', $user);
            exit;
        }

        deliver_response(400, 'Paramètre manquant (login ou all)');
        break;
    case 'POST':
        // if user admin verify token and can create admin user
        $newLogin = $input['login'] ?? null;
        $newMdp = $input['mdp'] ?? null;
        $newIsAdmin = isset($input['admin']) ? (bool)$input['admin'] : false;
        if (!$newLogin || !$newMdp) {
            deliver_response(400, 'login ou mdp manquant pour nouvel utilisateur');
            exit;
        }
        if (has_bearer_token()) {
            $payload = require_token_payload($secret);
            $isAdmin = !empty($payload['admin']);
        
            if ($newIsAdmin && !$isAdmin) {
                deliver_response(403, 'Seul un admin peut créer un utilisateur admin');
                exit;
            }
        } else {
            if ($newIsAdmin) {
                deliver_response(403, 'Seul un admin peut créer un utilisateur admin');
                exit;
            }
        }        
        
        if (check_user_exists($conn, $newLogin)) {
            deliver_response(409, 'Utilisateur déjà existant');
            exit;
        }
        $cle = getenv('PWD_KEY') ?: 'quoicoubeh';
        $mdp_hache = hash_hmac('sha256', $newMdp, $cle);
        //$mdp_hache = $newMdp;
        if (create_user($conn, $newLogin, $mdp_hache)) {
            // if admin can set admin flag
            if ($newIsAdmin) {
                // update user to set admin true
                $manager = $conn['manager'];
                $db = $conn['db'];
                $bulk = new MongoDB\Driver\BulkWrite();
                $bulk->update(['login' => $newLogin], ['$set' => ['admin' => true]]);
                try {
                    $manager->executeBulkWrite($db . '.user', $bulk);
                } catch (Exception $e) {
                    deliver_response(500, 'Erreur serveur lors de la mise à jour admin: ' . $e->getMessage());
                    exit;
                }
            }
            deliver_response(201, 'Utilisateur créé');
        } else {
            deliver_response(500, 'Erreur serveur lors de la création utilisateur');
        }
        break;  

    case 'DELETE':
        $payload = require_token_payload($secret);
        $isAdmin = isset($payload['admin']) && $payload['admin'];

        // target login can be in query or body
        $target = $_GET['login'] ?? ($input['login'] ?? null);
        if (!$target) {
            deliver_response(400, 'login cible manquant');
            exit;
        }

        if (!$isAdmin && ($payload['login'] ?? '') !== $target) {
            deliver_response(403, 'Non autorisé à supprimer cet utilisateur');
            exit;
        }

        // perform deletion
        $manager = $conn['manager'];
        $db = $conn['db'];
        $bulk = new MongoDB\Driver\BulkWrite();
        $bulk->delete(['login' => $target], ['limit' => 1]);
        try {
            $res = $manager->executeBulkWrite($db . '.user', $bulk);
            $deleted = $res->getDeletedCount();
            if ($deleted > 0) {
                deliver_response(200, 'Utilisateur supprimé');
            } else {
                deliver_response(404, 'Utilisateur non trouvé');
            }
        } catch (Exception $e) {
            deliver_response(500, 'Erreur serveur: ' . $e->getMessage());
        }
        break;

    default:
        deliver_response(405, 'Méthode non autorisée');
        break;
}
