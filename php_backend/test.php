<?php
// Test file to verify PHP setup and environment

header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');

// Test basic PHP functionality
$info = [
    'status' => 'ok',
    'php_version' => PHP_VERSION,
    'server_software' => $_SERVER['SERVER_SOFTWARE'] ?? 'Unknown',
    'request_method' => $_SERVER['REQUEST_METHOD'],
    'request_uri' => $_SERVER['REQUEST_URI'],
    'script_name' => $_SERVER['SCRIPT_NAME'],
    'document_root' => $_SERVER['DOCUMENT_ROOT'] ?? 'Unknown',
    'current_dir' => __DIR__,
];

// Test if config.php can be loaded
$info['config_exists'] = file_exists(__DIR__ . '/config.php');
$info['env_exists'] = file_exists(__DIR__ . '/.env');
$info['supabase_client_exists'] = file_exists(__DIR__ . '/SupabaseClient.php');

// Try to load config
if ($info['config_exists']) {
    try {
        require_once 'config.php';
        $info['supabase_url_set'] = !empty(SUPABASE_URL);
        $info['supabase_key_set'] = !empty(SUPABASE_KEY);
        $info['supabase_url_length'] = strlen(SUPABASE_URL);
    } catch (Exception $e) {
        $info['config_error'] = $e->getMessage();
    }
}

// Test if mod_rewrite is available
$info['mod_rewrite'] = in_array('mod_rewrite', apache_get_modules() ?? []);

// Test file permissions
if ($info['env_exists']) {
    $info['env_readable'] = is_readable(__DIR__ . '/.env');
    $info['env_permissions'] = substr(sprintf('%o', fileperms(__DIR__ . '/.env')), -4);
}

echo json_encode($info, JSON_PRETTY_PRINT);