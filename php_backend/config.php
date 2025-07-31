<?php

// Load environment variables
if (file_exists(__DIR__ . '/.env')) {
    $envFile = @file(__DIR__ . '/.env', FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);
    if ($envFile === false) {
        error_log('Warning: Could not read .env file. Check file permissions.');
    } else {
        foreach ($envFile as $line) {
            if (strpos($line, '=') !== false && strpos($line, '#') !== 0) {
                list($key, $value) = explode('=', $line, 2);
                $key = trim($key);
                $value = trim($value);
                
                // Remove quotes if present
                if ((substr($value, 0, 1) === '"' && substr($value, -1) === '"') ||
                    (substr($value, 0, 1) === "'" && substr($value, -1) === "'")) {
                    $value = substr($value, 1, -1);
                }
                
                if (function_exists('putenv')) {
                    putenv("$key=$value");
                }
                $_ENV[$key] = $value;
                $_SERVER[$key] = $value;
            }
        }
    }
}

// Define constants from environment variables (check multiple sources)
define('SUPABASE_URL', getenv('SUPABASE_URL') ?: ($_ENV['SUPABASE_URL'] ?? ($_SERVER['SUPABASE_URL'] ?? '')));
define('SUPABASE_KEY', getenv('SUPABASE_KEY') ?: ($_ENV['SUPABASE_KEY'] ?? ($_SERVER['SUPABASE_KEY'] ?? '')));

// Validate required configuration
if (empty(SUPABASE_URL) || empty(SUPABASE_KEY)) {
    error_log('Missing required environment variables: SUPABASE_URL or SUPABASE_KEY');
    if (php_sapi_name() !== 'cli') {
        http_response_code(500);
        echo json_encode(['error' => 'Server configuration error']);
        exit();
    }
}

// Set timezone
date_default_timezone_set('UTC');

// Error reporting settings
if (getenv('APP_ENV') === 'production') {
    error_reporting(E_ALL & ~E_NOTICE & ~E_DEPRECATED);
    ini_set('display_errors', '0');
} else {
    error_reporting(E_ALL);
    ini_set('display_errors', '1');
}

// Set error log
ini_set('error_log', __DIR__ . '/error.log');