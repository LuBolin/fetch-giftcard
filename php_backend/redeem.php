<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(204);
    exit();
}

require_once 'config.php';
require_once 'SupabaseClient.php';

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['success' => false, 'message' => 'Method not allowed']);
    exit();
}

$inputData = json_decode(file_get_contents('php://input'), true);
error_log("Received data: " . json_encode($inputData));

$code = $inputData['code'] ?? null;
$recipient_email = $inputData['recipient_email'] ?? null;
$recipient_phone = $inputData['recipient_phone'] ?? null;
$metadata = $inputData['metadata'] ?? [];

error_log("Parsed - code: $code, email: $recipient_email, phone: $recipient_phone");

if (!$code || !$recipient_email || !$recipient_phone) {
    http_response_code(400);
    echo json_encode(['success' => false, 'message' => 'Missing code or recipient information']);
    exit();
}

try {
    $supabase = new SupabaseClient(SUPABASE_URL, SUPABASE_KEY);
    $supabase->redeemCode($code, $recipient_email, $recipient_phone, $metadata);
    
    echo json_encode([
        'success' => true,
        'message' => 'Code redeemed successfully!'
    ]);
    
} catch (Exception $e) {
    error_log('Error in redeem_endpoint: ' . get_class($e) . ': ' . $e->getMessage());
    http_response_code(500);
    echo json_encode(['success' => false, 'message' => 'Server error: ' . $e->getMessage()]);
}