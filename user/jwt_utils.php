<?php

function generate_jwt($headers, $payload, $secret) {
    // Encode l'en-tête et le payload en base64 URL-safe
    $headers_encoded = base64url_encode(json_encode($headers));
    $payload_encoded = base64url_encode(json_encode($payload));

    // Génère la signature avec HMAC-SHA256
    $signature = hash_hmac('SHA256', "$headers_encoded.$payload_encoded", $secret, true);
    $signature_encoded = base64url_encode($signature);

    // Assemble le JWT final
    return "$headers_encoded.$payload_encoded.$signature_encoded";
}

function is_jwt_valid($jwt, $secret) {
    // Sépare les parties du token
    $tokenParts = explode('.', $jwt);
    $header = base64_decode($tokenParts[0]);
    $payload = base64_decode($tokenParts[1]);
    $signature_provided = $tokenParts[2];

    // Vérifie l'expiration du token
    $expiration = json_decode($payload)->exp;
    $is_token_expired = ($expiration - time()) < 0;

    // Regénère la signature et la compare avec celle fournie
    $base64_url_header = base64url_encode($header);
    $base64_url_payload = base64url_encode($payload);
    $signature = hash_hmac('SHA256', "$base64_url_header.$base64_url_payload", $secret, true);
    $base64_url_signature = base64url_encode($signature);

    // Vérifie si le token est valide
    return !$is_token_expired && ($base64_url_signature === $signature_provided);
}

function base64url_encode($data) {
    // Encode en base64 et rend l'encodage URL-safe
    return rtrim(strtr(base64_encode($data), '+/', '-_'), '=');
}

function get_authorization_header() {
    // Récupère l'en-tête Authorization, compatible avec différents serveurs
    if (isset($_SERVER['Authorization'])) {
        return trim($_SERVER["Authorization"]);
    } elseif (isset($_SERVER['HTTP_AUTHORIZATION'])) {
        return trim($_SERVER["HTTP_AUTHORIZATION"]);
    } elseif (function_exists('apache_request_headers')) {
        $requestHeaders = apache_request_headers();
        $requestHeaders = array_combine(array_map('ucwords', array_keys($requestHeaders)), array_values($requestHeaders));
        return isset($requestHeaders['Authorization']) ? trim($requestHeaders['Authorization']) : null;
    }
    return null;
}

function get_bearer_token() {
    // Extrait le token Bearer de l'en-tête Authorization
    $headers = get_authorization_header();
    if (!empty($headers) && preg_match('/Bearer\s(\S+)/', $headers, $matches)) {
        return $matches[1] === 'null' ? null : $matches[1];
    }
    return null;
}

?>