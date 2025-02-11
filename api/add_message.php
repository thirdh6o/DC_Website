<?php
require_once 'config.php';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $data = json_decode(file_get_contents('php://input'), true);
    
    if (!empty($data['name']) && !empty($data['message'])) {
        try {
            $stmt = $pdo->prepare("INSERT INTO messages (name, avatar, message) VALUES (?, ?, ?)");
            $avatar = "https://api.dicebear.com/7.x/avataaars/svg?seed=" . time();
            $stmt->execute([$data['name'], $avatar, $data['message']]);
            
            echo json_encode([
                'success' => true,
                'message' => 'Message added successfully'
            ]);
        } catch(PDOException $e) {
            echo json_encode(['error' => $e->getMessage()]);
        }
    } else {
        echo json_encode(['error' => 'Name and message are required']);
    }
} 