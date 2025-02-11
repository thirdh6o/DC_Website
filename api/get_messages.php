<?php
require_once 'config.php';

try {
    $stmt = $pdo->query("SELECT * FROM messages ORDER BY created_at DESC");
    $messages = $stmt->fetchAll(PDO::FETCH_ASSOC);
    echo json_encode(['success' => true, 'messages' => $messages]);
} catch(PDOException $e) {
    echo json_encode(['error' => $e->getMessage()]);
} 