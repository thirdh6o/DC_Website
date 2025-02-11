<?php
// 添加缓存控制头
header('Cache-Control: no-store, no-cache, must-revalidate, max-age=0');
header('Cache-Control: post-check=0, pre-check=0', false);
header('Pragma: no-cache');
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST');
header('Access-Control-Allow-Headers: Content-Type');

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if (isset($_FILES['photo'])) {
        // 创建上传目录
        $upload_dir = '../uploads/';
        $processed_dir = '../uploads/processed/';
        $info_dir = '../uploads/info/';
        
        foreach ([$upload_dir, $processed_dir, $info_dir] as $dir) {
            if (!file_exists($dir)) {
                mkdir($dir, 0777, true);
            }
        }

        // 生成唯一文件名
        $timestamp = time();
        $original_name = $_FILES['photo']['name'];
        $extension = pathinfo($original_name, PATHINFO_EXTENSION);
        $filename = $timestamp . '_' . uniqid() . '.' . $extension;
        
        $upload_path = $upload_dir . $filename;
        $processed_path = $processed_dir . $filename;

        // 保存上传的文件
        if (move_uploaded_file($_FILES['photo']['tmp_name'], $upload_path)) {
            // 调用Python脚本处理图片
            $command = "python3 " . __DIR__ . "/process_image.py " . 
                       escapeshellarg($upload_path) . " " . 
                       escapeshellarg($processed_path) . " " .
                       escapeshellarg($info_dir);
            
            exec($command, $output, $return_var);

            if ($return_var !== 0) {
                throw new Exception('Image processing failed');
            }

            // 处理图片（这里可以调用其他处理函数）
            $processedImageUrl = 'https://你的服务器地址/uploads/' . $filename; // 假设处理后的图片路径

            echo json_encode(['success' => true, 'processedImage' => $processedImageUrl]);
        } else {
            echo json_encode(['success' => false, 'error' => 'Failed to save uploaded file']);
        }
    } else {
        echo json_encode(['success' => false, 'error' => 'No file uploaded']);
    }
} else {
    echo json_encode(['success' => false, 'error' => 'Invalid request method']);
} 