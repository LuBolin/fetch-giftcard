<?php
require_once 'config.php';

// Get the request URI
$requestUri = $_SERVER['REQUEST_URI'];
$requestMethod = $_SERVER['REQUEST_METHOD'];

// Remove query string and base path if needed
$path = strtok($requestUri, '?');
$basePath = dirname($_SERVER['SCRIPT_NAME']);
if ($basePath !== '/') {
    $path = str_replace($basePath, '', $path);
}
$path = '/' . ltrim($path, '/');

// Route handling
if ($path === '/redeem') {
    require_once 'redeem.php';
    exit();
}

// Serve frontend files
$frontendPath = dirname(__DIR__) . '/frontend';

// Map routes to frontend files
$routes = [
    '/' => '/redeem.html',
    '/index.html' => '/redeem.html',
    '/redeem.html' => '/redeem.html',
    '/redeem.css' => '/redeem.css',
    '/redeem.js' => '/redeem.js'
];

if (isset($routes[$path])) {
    $file = $frontendPath . $routes[$path];
    
    if (file_exists($file)) {
        // Set appropriate content type
        $extension = pathinfo($file, PATHINFO_EXTENSION);
        $contentTypes = [
            'html' => 'text/html',
            'css' => 'text/css',
            'js' => 'application/javascript'
        ];
        
        if (isset($contentTypes[$extension])) {
            header('Content-Type: ' . $contentTypes[$extension]);
        }
        
        readfile($file);
        exit();
    }
}

// 404 for unmatched routes
http_response_code(404);
echo json_encode(['error' => 'Not found']);