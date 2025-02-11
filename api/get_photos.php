<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

$infoDir = '../uploads/info/';
$photos = [];

// 读取所有图片信息文件
if (is_dir($infoDir)) {
    $files = glob($infoDir . '*.json');
    
    foreach ($files as $file) {
        $photoInfo = json_decode(file_get_contents($file), true);
        if ($photoInfo) {
            $photos[] = $photoInfo;
        }
    }
}

// 按时间倒序排序
usort($photos, function($a, $b) {
    return strtotime($b['created_at']) - strtotime($a['created_at']);
});

// 如果照片数量超过10张，随机选择10张
if (count($photos) > 10) {
    shuffle($photos);
    $photos = array_slice($photos, 0, 10);
}

echo json_encode([
    'success' => true,
    'photos' => $photos
]); 