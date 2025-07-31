<?php

class SupabaseClient {
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

    private function makeRequest($method, $endpoint, $data = null, $params = []) {
        $url = $this->supabaseUrl . '/rest/v1/' . $endpoint;
        
        if (!empty($params)) {
            $url .= '?' . http_build_query($params);
        }
        
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
        $error = curl_error($ch);
        curl_close($ch);
        
        if ($error) {
            throw new Exception('cURL error: ' . $error);
        }
        
        if ($httpCode >= 400) {
            $errorData = json_decode($response, true);
            throw new Exception('Supabase error: ' . ($errorData['message'] ?? 'Unknown error'));
        }
        
        return json_decode($response, true);
    }

    public function uploadCodes($codes, $metadata = null) {
        $bulkData = [];
        foreach ($codes as $code) {
            $data = [
                'code' => $code,
                'metadata' => $metadata
            ];
            $bulkData[] = $data;
        }

        try {
            $response = $this->makeRequest('POST', 'gift_codes', $bulkData);
            error_log("✅ Successfully inserted " . count($codes) . " codes in bulk");
            return $response;
        } catch (Exception $e) {
            error_log("❌ Error bulk inserting codes: " . $e->getMessage());
            throw $e;
        }
    }

    public function redeemCode($code, $recipientEmail, $recipientPhone, $metadata = null) {
        $params = ['code' => 'eq.' . $code];
        $checkRes = $this->makeRequest('GET', 'gift_codes', null, $params);
        
        if (empty($checkRes)) {
            throw new Exception("Code '$code' not found in database.");
        }

        $row = $checkRes[0];
        if ($row['is_redeemed'] ?? false) {
            throw new Exception("Code '$code' has already been redeemed.");
        }
        
        $expiryDate = $row['expiry_date'] ?? null;
        if ($expiryDate) {
            $expiryDateObj = new DateTime($expiryDate);
            $today = new DateTime();
            $today->setTime(0, 0, 0);
            
            if ($today > $expiryDateObj) {
                throw new Exception("Code '$code' has expired on " . $expiryDateObj->format('Y-m-d') . ".");
            }
        }

        $utcTime = new DateTime('now', new DateTimeZone('UTC'));
        $data = [
            'is_redeemed' => true,
            'redeemed_at' => $utcTime->format('Y-m-d\TH:i:s.u\Z'),
            'recipient_email' => $recipientEmail,
            'recipient_phone' => $recipientPhone,
            'metadata' => $metadata
        ];
        
        try {
            $params = [
                'code' => 'eq.' . $code,
                'is_redeemed' => 'eq.false'
            ];
            $response = $this->makeRequest('PATCH', 'gift_codes', $data, $params);
            
            if (empty($response)) {
                throw new Exception("Code $code not found or already redeemed.");
            }
            
            $updatedRow = $response[0];
            error_log("✅ Redeemed $code for email $recipientEmail");
            error_log("Updated row: " . json_encode($updatedRow));
            
            return $updatedRow;
        } catch (Exception $e) {
            throw $e;
        }
    }
    
    public function resetCode($code) {
        try {
            $data = [
                'is_redeemed' => false,
                'recipient_email' => null,
                'recipient_phone' => null,
                'redeemed_at' => null
            ];
            $params = ['code' => 'eq.' . $code];
            $response = $this->makeRequest('PATCH', 'gift_codes', $data, $params);
            
            if (!empty($response)) {
                error_log("✅ Reset $code successfully.");
            } else {
                error_log("❌ Code $code not found or not redeemed.");
            }
        } catch (Exception $e) {
            error_log("❌ Error resetting $code: " . $e->getMessage());
        }
    }

    public function updateExpiry($startSerial, $endSerial, $newExpiryDate) {
        try {
            if ($newExpiryDate instanceof DateTime) {
                $expiryValue = $newExpiryDate->format('Y-m-d');
            } else {
                $expiryValue = $newExpiryDate;
            }
                
            $data = ['expiry_date' => $expiryValue];
            $params = [
                'serial_number' => 'gte.' . $startSerial,
                'serial_number' => 'lte.' . $endSerial,
                'is_redeemed' => 'eq.false'
            ];
            
            $response = $this->makeRequest('PATCH', 'gift_codes', $data, $params);

            if (!empty($response)) {
                error_log("✅ Updated expiry date for codes from $startSerial to $endSerial.");
            } else {
                error_log("❌ No codes found in the range $startSerial to $endSerial that are not redeemed.");
            }
        } catch (Exception $e) {
            error_log("❌ Error updating expiry date: " . $e->getMessage());
        }
    }
    
    public function distributeCards($startSerial, $endSerial, $distributedTo, $distributedAt = null) {
        if ($distributedAt === null) {
            $utcTime = new DateTime('now', new DateTimeZone('UTC'));
            $distributedAt = $utcTime->format('Y-m-d\TH:i:s.u\Z');
        }
        
        try {
            $data = [
                'distributed_to' => $distributedTo,
                'distributed_at' => $distributedAt
            ];
            $params = [
                'serial_number' => 'gte.' . $startSerial,
                'serial_number' => 'lte.' . $endSerial,
                'is_redeemed' => 'eq.false'
            ];
            
            $response = $this->makeRequest('PATCH', 'gift_codes', $data, $params);

            if (!empty($response)) {
                error_log("✅ Distributed codes from $startSerial to $endSerial to $distributedTo.");
            } else {
                error_log("❌ No codes found in the range $startSerial to $endSerial that are not redeemed.");
            }
        } catch (Exception $e) {
            error_log("❌ Error distributing cards: " . $e->getMessage());
        }
    }
}