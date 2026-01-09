<?php
require_once 'jwt_utils.php';
require_once 'connectionbd.php';
require_once 'function.php';

$method = $_SERVER['REQUEST_METHOD'];
$input = json_decode(file_get_contents('php://input'), true);

switch ($method) {
    case 'GET' :
        // Vérifie la présence du token JWT
        if(!get_bearer_token()){
            deliver_response(401, "Vous n'avez pas fourni de token");
            exit;
        }

        // secret configurable via variable d'environnement
        $secret = getenv('JWT_SECRET') ?: 'coucou_je_suis_secret';
        $token = get_bearer_token();

        // Vérifie la validité du token
        if (is_jwt_valid($token, $secret)) {
            deliver_response(200, 'Token valide.');
        } else {
            deliver_response(401, 'Token invalide.');
        }
        break;
    
    case 'POST':
        // Vérifie les identifiants et génère un JWT si valides
        if (isset($input['login']) && isset($input['mdp'])) {
            $login = $input['login'];
            $mdp = $input['mdp'];

            if ($login === '' || $mdp === '') {
                deliver_response(400, 'Identifiant ou mot de passe vide');
                exit;
            }

            // clé de hachage configurable
            $cle = getenv('PWD_KEY') ?: 'quoicoubeh';

            //$mdp_hache = hash_hmac('sha256', $mdp, $cle);
            $mdp_hache = $mdp;

            try {
                // connectionToDB() retourne ['manager' => Manager, 'db' => 'dbname']
                $conn = connectionToDB();

                // Vérifie si l'utilisateur existe
                if (!check_user_exists($conn, $login)) {
                    deliver_response(404, 'Utilisateur non trouvé.');
                    exit;
                }

                $user = getUser($conn, $login);

                // Vérifie si le mot de passe est correct
                if (!$user || $mdp_hache !== $user['mdp']) {
                    deliver_response(401, 'Identifiant ou mot de passe incorrect.');
                    exit;
                }

                // Génération du token JWT pour l'utilisateur authentifié
                $headers = ['alg' => 'HS256', 'typ' => 'JWT'];
                $payload = ['login' => $login, 'exp' => (time() + 86400)];
                $secret = getenv('JWT_SECRET') ?: 'coucou_je_suis_secret';

                $jwt = generate_jwt($headers, $payload, $secret);

                // Envoi du token en réponse
                deliver_response(200, 'OK', ['token' => $jwt]);
            } catch (Exception $e) {
                error_log("Erreur serveur: " . $e->getMessage());

                deliver_response(500,$e->getMessage());

            }
        } else {
            deliver_response(400, 'Identifiant ou mot de passe manquant');
        }
        break;
    
    default:
        // Méthode HTTP non autorisée
        deliver_response(405, 'Méthode non autorisée.');
        break;
}
?>