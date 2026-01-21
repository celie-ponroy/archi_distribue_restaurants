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
    if (count($tokenParts) !== 3) return false;

    $header_b64 = $tokenParts[0];
    $payload_b64 = $tokenParts[1];
    $signature_provided = $tokenParts[2];

    // Decode payload to check expiration safely
    $payload_json = base64url_decode($payload_b64);
    $payload_obj = json_decode($payload_json);
    if (!$payload_obj || !isset($payload_obj->exp)) return false;

    $is_token_expired = ($payload_obj->exp - time()) < 0;

    // Regénère la signature et la compare avec celle fournie
    $signature = hash_hmac('SHA256', "$header_b64.$payload_b64", $secret, true);
    $base64_url_signature = base64url_encode($signature);

    return !$is_token_expired && ($base64_url_signature === $signature_provided);
}

function base64url_encode($data) {
    // Encode en base64 et rend l'encodage URL-safe
    return rtrim(strtr(base64_encode($data), '+/', '-_'), '=');
}

function base64url_decode($data) {
    $remainder = strlen($data) % 4;
    if ($remainder) {
        $padlen = 4 - $remainder;
        $data .= str_repeat('=', $padlen);
    }
    $decoded = base64_decode(strtr($data, '-_', '+/'));
    return $decoded;
}

/**
 * Decode a JWT and return the payload as associative array (or null on failure)
 */
function decode_jwt_payload($jwt) {
    $parts = explode('.', $jwt);
    if (count($parts) !== 3) return null;
    $payload_json = base64url_decode($parts[1]);
    $payload = json_decode($payload_json, true);
    return $payload;
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

