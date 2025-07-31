<?php

class SupabaseTool {
    private $supabaseUrl;
    private $supabaseKey;
    private $headers;

    public function __construct($url, $key) {
        $this->supabaseUrl = rtrim($url, '/');
        $this->supabaseKey = $key;
        $this->headers = [
            'apikey: ' . $this->supabaseKey,
            'Authorization: Bearer ' . $this->supabaseKey,
            'Content-Type: application/json',
            'Prefer: return=representation'
        ];
    }

    private function makeRequest($method, $endpoint, $data = null) {
        $url = $this->supabaseUrl . '/rest/v1/' . $endpoint;
        
        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, $url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_HTTPHEADER, $this->headers);
        curl_setopt($ch, CURLOPT_CUSTOMREQUEST, $method);
        
        if ($data !== null) {
            curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
        }
        
        $response = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);
        
        if ($httpCode >= 400) {
            $error = json_decode($response, true);
            throw new Exception('Supabase error: ' . ($error['message'] ?? 'Unknown error'));
        }
        
        return json_decode($response, true);
    }

    public function checkCodeValidity($code) {
        $endpoint = 'unique_codes?unique_code=eq.' . urlencode($code);
        $result = $this->makeRequest('GET', $endpoint);
        
        if (empty($result)) {
            return ['valid' => false, 'message' => 'Invalid code'];
        }
        
        $codeData = $result[0];
        
        if ($codeData['is_redeemed']) {
            return ['valid' => false, 'message' => 'Code has already been redeemed'];
        }
        
        if (!empty($codeData['expiry_date'])) {
            $expiryDate = new DateTime($codeData['expiry_date']);
            $today = new DateTime();
            if ($expiryDate < $today) {
                return ['valid' => false, 'message' => 'Code has expired'];
            }
        }
        
        return [
            'valid' => true,
            'amount' => $codeData['amount'],
            'id' => $codeData['id']
        ];
    }

    public function redeemCode($codeId, $email) {
        $endpoint = 'unique_codes?id=eq.' . urlencode($codeId);
        $data = [
            'is_redeemed' => true,
            'redeemed_at' => gmdate('Y-m-d\TH:i:s\Z'),
            'used_email' => $email
        ];
        
        $result = $this->makeRequest('PATCH', $endpoint, $data);
        
        if (empty($result)) {
            throw new Exception('Failed to update code status');
        }
        
        return true;
    }

    public function insertCode($uniqueCode, $amount, $expiryDate = null, $createdBy = 'system', $batchId = null, $notes = null) {
        $data = [
            'unique_code' => $uniqueCode,
            'amount' => $amount,
            'is_redeemed' => false,
            'created_by' => $createdBy
        ];
        
        if ($expiryDate !== null) {
            $data['expiry_date'] = $expiryDate;
        }
        
        if ($batchId !== null) {
            $data['batch_id'] = $batchId;
        }
        
        if ($notes !== null) {
            $data['notes'] = $notes;
        }
        
        return $this->makeRequest('POST', 'unique_codes', $data);
    }

    public function bulkInsertCodes($codes) {
        return $this->makeRequest('POST', 'unique_codes', $codes);
    }

    public function getRedeemedCodes($startDate = null, $endDate = null) {
        $endpoint = 'unique_codes?is_redeemed=eq.true';
        
        if ($startDate !== null) {
            $endpoint .= '&redeemed_at=gte.' . urlencode($startDate);
        }
        
        if ($endDate !== null) {
            $endpoint .= '&redeemed_at=lte.' . urlencode($endDate);
        }
        
        $endpoint .= '&order=redeemed_at.desc';
        
        return $this->makeRequest('GET', $endpoint);
    }

    public function getUnredeemedCodes() {
        $endpoint = 'unique_codes?is_redeemed=eq.false&order=created_at.desc';
        return $this->makeRequest('GET', $endpoint);
    }

    public function getCodesByBatch($batchId) {
        $endpoint = 'unique_codes?batch_id=eq.' . urlencode($batchId);
        return $this->makeRequest('GET', $endpoint);
    }

    public function deleteCode($codeId) {
        $endpoint = 'unique_codes?id=eq.' . urlencode($codeId);
        return $this->makeRequest('DELETE', $endpoint);
    }

    public function updateCodeExpiry($codeId, $newExpiryDate) {
        $endpoint = 'unique_codes?id=eq.' . urlencode($codeId);
        $data = ['expiry_date' => $newExpiryDate];
        return $this->makeRequest('PATCH', $endpoint, $data);
    }

    public function getCodeStats() {
        $totalCodes = $this->makeRequest('GET', 'unique_codes?select=count');
        $redeemedCodes = $this->makeRequest('GET', 'unique_codes?is_redeemed=eq.true&select=count');
        $totalAmount = $this->makeRequest('GET', 'unique_codes?select=amount.sum');
        $redeemedAmount = $this->makeRequest('GET', 'unique_codes?is_redeemed=eq.true&select=amount.sum');
        
        return [
            'total_codes' => $totalCodes[0]['count'] ?? 0,
            'redeemed_codes' => $redeemedCodes[0]['count'] ?? 0,
            'total_amount' => $totalAmount[0]['sum'] ?? 0,
            'redeemed_amount' => $redeemedAmount[0]['sum'] ?? 0
        ];
    }
}